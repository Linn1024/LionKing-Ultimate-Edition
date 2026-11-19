"""Add opt-in copied WRAM/input-index snapshots to the read-only player host."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_rng_allbugs.py')
source=original_builder.read_text()
source=source.replace("out=parent/'allbugs-observer'", "out=parent/'width-observer'")
snapshot=r'''
    const char *fields=getenv("TLK_OBS_DUMP_FIELDS"),*directory=getenv("TLK_OBS_DUMP_DIR");
    if(fields && directory) {
        const char *at=fields;
        while(*at) {
            char *end;
            unsigned selected=(unsigned)strtoul(at,&end,10);
            if(end==at)exit(96);
            if(selected==(unsigned)snes_frame_counter) {
                char path[4096];
                snprintf(path,sizeof path,"%s/wram-%u.bin",directory,selected);
                FILE *f=fopen(path,"wb");if(!f)exit(96);
                if(fwrite(g_ram,1,0x20000,f)!=0x20000)exit(96);fclose(f);
                snprintf(path,sizeof path,"%s/input-%u.csv",directory,selected);
                f=fopen(path,"w");if(!f)exit(96);
                fprintf(f,"field,polls_used\n%u,%u\n",selected,(unsigned)s_poll_idx);fclose(f);
            }
            at=end;if(*at==',')at++;else if(*at)exit(96);
        }
    }
'''
anchor='    return result;\n}\n'
assert source.count(anchor)==1
source=source.replace(anchor,snapshot+anchor)
source=source.replace('paths=[Path(__file__),bp,original,source,backend,',
                      'paths=[Path(__file__),original_builder,bp,original,source,backend,')
exec(compile(source,str(original_builder),'exec'))
