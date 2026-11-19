/* Factory-owned second draw uses actor+28, not the usual actor+8. */
static unsigned TlkGraveyardPillarOwner(const uint8_t *ram,unsigned obj,unsigned pose) {
    if(!ram || pose!=0x7eab06 || obj>0xffe8 || rd24(ram+0xdf)!=0xc003eb)return 0;
    unsigned position=rd16(ram+obj+4);
    for(unsigned offset=8;offset<=28;offset+=20) {
        if(position<0x8000+offset || position>0xff80+offset)continue;
        unsigned actor=position-offset,primary=rd16(ram+actor+12);
        if(rd24(ram+actor+4)!=0xc58d44 || primary>0xffe8 ||
           rd16(ram+primary+4)!=actor+8 || rd24(ram+primary+10)!=pose)continue;
        unsigned action=rd24(ram+actor+48);
        if(action!=0xc2d13d && action!=0xc2d1d3)continue;
        if(offset==8 && primary==obj)return actor;
        if(offset==28 && rd24(ram+actor+36)==(0x7e0000|obj) &&
           rd16(ram+actor+28)==(uint16_t)(rd16(ram+actor+8)+48) &&
           rd16(ram+actor+30)==rd16(ram+actor+10) && rd24(ram+obj+10)==pose)return actor;
    }
    return 0;
}
