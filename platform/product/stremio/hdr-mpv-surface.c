#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <dlfcn.h>
#include <elf.h>
#include <link.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdatomic.h>
extern int __android_log_print(int,const char *,const char *,...);
extern int32_t ANativeWindow_getBuffersDataSpace(void *);
static _Atomic int hdr_enabled;
static void *(*original_create)(void *,void *,void *,const int32_t *);
static int32_t (*config_attrib)(void *,void *,int32_t,int32_t *);
static int hooked;
static void *create_surface(void *display,void *config,void *window,const int32_t *attributes) {
    if (!atomic_load(&hdr_enabled)) return original_create(display,config,window,attributes);
    int32_t hdr_attributes[128]; unsigned size=0;
    if (attributes) {
        for (unsigned index=0;index<120 && attributes[index]!=0x3038;index+=2) {
            if (attributes[index]==0x309d) continue;
            hdr_attributes[size++]=attributes[index];
            hdr_attributes[size++]=attributes[index+1];
        }
    }
    hdr_attributes[size++]=0x309d; hdr_attributes[size++]=0x3340; hdr_attributes[size]=0x3038;
    void *surface=original_create(display,config,window,hdr_attributes);
    int32_t red_bits=0;
    if (config_attrib) config_attrib(display,config,0x3024,&red_bits);
    __android_log_print(4,"NucHdrSurface","MPV PQ surface=%p red_bits=%d dataspace=0x%x",surface,red_bits,ANativeWindow_getBuffersDataSpace(window));
    return surface;
}
static uintptr_t address(uintptr_t base,uintptr_t value) { return value<base?base+value:value; }
static int hook_mpv(struct dl_phdr_info *info,size_t size,void *argument) {
    (void)size;(void)argument;
    if (!info->dlpi_name || !strstr(info->dlpi_name,"/libmpv.so")) return 0;
    const Elf64_Dyn *dynamic=NULL;
    for (int n=0;n<info->dlpi_phnum;n++)
        if (info->dlpi_phdr[n].p_type==PT_DYNAMIC) dynamic=(void *)(info->dlpi_addr+info->dlpi_phdr[n].p_vaddr);
    if (!dynamic) return 1;
    const char *strings=NULL;const Elf64_Sym *symbols=NULL;const Elf64_Rela *relocations=NULL;
    size_t relocation_size=0;int kind=0;
    for (const Elf64_Dyn *d=dynamic;d->d_tag!=DT_NULL;d++) {
        if (d->d_tag==DT_STRTAB) strings=(void *)address(info->dlpi_addr,d->d_un.d_ptr);
        if (d->d_tag==DT_SYMTAB) symbols=(void *)address(info->dlpi_addr,d->d_un.d_ptr);
        if (d->d_tag==DT_JMPREL) relocations=(void *)address(info->dlpi_addr,d->d_un.d_ptr);
        if (d->d_tag==DT_PLTRELSZ) relocation_size=d->d_un.d_val;
        if (d->d_tag==DT_PLTREL) kind=d->d_un.d_val;
    }
    if (!strings || !symbols || !relocations || kind!=DT_RELA) return 1;
    for (size_t i=0;i<relocation_size/sizeof(*relocations);i++) {
        const Elf64_Rela *r=relocations+i;
        if (ELF64_R_TYPE(r->r_info)!=R_X86_64_JUMP_SLOT) continue;
        if (strcmp(strings+symbols[ELF64_R_SYM(r->r_info)].st_name,"eglCreateWindowSurface")) continue;
        void **slot=(void **)(info->dlpi_addr+r->r_offset);
        original_create=*slot;
        size_t page_size=getpagesize();void *page=(void *)((uintptr_t)slot&~(page_size-1));
        if (mprotect(page,page_size,PROT_READ|PROT_WRITE)) return 1;
        *slot=(void *)create_surface;
        if (mprotect(page,page_size,PROT_READ)) return 1;
        hooked=1;
    }
    return 1;
}
__attribute__((visibility("default")))
int32_t Java_local_nuc_player_PlayerActivity_nativeHdrSurface(void *env,void *type,uint8_t enabled) {
    (void)env;(void)type;
    if (enabled && !hooked) {
        void *egl=dlopen("libEGL.so",RTLD_NOW|RTLD_LOCAL);
        if (egl) config_attrib=dlsym(egl,"eglGetConfigAttrib");
        dl_iterate_phdr(hook_mpv,NULL);
    }
    atomic_store(&hdr_enabled,enabled && hooked);
    return enabled && !hooked ? -1 : 0;
}
