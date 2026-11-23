#pragma once
#include <algorithm>
#include <cstdint>
#include <cstddef>
#include <vector>

/* A colour is an identity, never a position in a pose's pixel traversal. */
struct BrowserPaletteModel {
    std::vector<uint16_t> colours[2];
    std::vector<uint16_t> original_colours[2];
    int selected[2] = {-1, -1};
    struct Bounds { unsigned left=0,top=0,right=0,bottom=0; } bounds[2];

    static uint16_t Colour(uint32_t pixel) {
        return (uint16_t)((pixel>>19&31) | (pixel>>11&31)<<5 | (pixel>>3&31)<<10);
    }
    static bool Before(uint16_t a,uint16_t b) {
        unsigned light_a=(a&31)*299+(a>>5&31)*587+(a>>10&31)*114;
        unsigned light_b=(b&31)*299+(b>>5&31)*587+(b>>10&31)*114;
        return light_a==light_b ? a<b : light_a<light_b;
    }
    void Clear() {
        for(auto &c:colours)c.clear();
        for(auto &c:original_colours)c.clear();
        selected[0]=selected[1]=-1;bounds[0]={};bounds[1]={};
    }
    void Merge(int source,const std::vector<uint16_t> &extra) {
        auto &c=colours[source];c.insert(c.end(),extra.begin(),extra.end());
        std::sort(c.begin(),c.end());c.erase(std::unique(c.begin(),c.end()),c.end());
        std::sort(c.begin(),c.end(),Before);
        if(selected[source]<0&&!c.empty())selected[source]=c.front();
    }
    void Observe(int source,const std::vector<uint16_t> &extra) {
        auto &base=original_colours[source];base.insert(base.end(),extra.begin(),extra.end());
        std::sort(base.begin(),base.end());base.erase(std::unique(base.begin(),base.end()),base.end());
        std::sort(base.begin(),base.end(),Before);Merge(source,extra);
    }
    void ResetSource(int source) {
        colours[source]=original_colours[source];
        if(std::find(colours[source].begin(),colours[source].end(),selected[source])==colours[source].end())
            selected[source]=colours[source].empty()?-1:colours[source].front();
    }
    void Build(const uint32_t *pixels,unsigned width,unsigned height,unsigned frames,unsigned planes) {
        if(!pixels||!width||!height||!frames||(planes!=2&&planes!=4))return;
        for(unsigned source=0;source<2;source++) {
            bool used[32768]={};Bounds box{width,height,0,0};
            for(unsigned frame=0;frame<frames;frame++)for(unsigned axis=source;axis<planes;axis+=2) {
                const uint32_t *p=pixels+((size_t)frame*planes+axis)*width*height;
                for(unsigned y=0;y<height;y++)for(unsigned x=0;x<width;x++)if(p[(size_t)y*width+x]>>24) {
                    used[Colour(p[(size_t)y*width+x])]=true;
                    box.left=std::min(box.left,x);box.top=std::min(box.top,y);
                    box.right=std::max(box.right,x+1);box.bottom=std::max(box.bottom,y+1);
                }
            }
            std::vector<uint16_t> all;
            for(unsigned c=0;c<32768;c++)if(used[c])all.push_back((uint16_t)c);
            Observe((int)source,all);
            if(box.left>=box.right)box={0,0,width,height};
            else {box.left=box.left>6?box.left-6:0;box.top=box.top>6?box.top-6:0;
                box.right=std::min(width,box.right+6);box.bottom=std::min(height,box.bottom+6);}
            bounds[source]=box;
        }
    }
    static bool Uses(const uint32_t *pixels,size_t count,uint16_t colour) {
        for(size_t i=0;i<count;i++)if((pixels[i]>>24)&&Colour(pixels[i])==colour)return true;
        return false;
    }
    static int FindPose(const uint32_t *pixels,unsigned width,unsigned height,unsigned frames,
                        unsigned planes,unsigned axis,uint16_t colour,unsigned after) {
        for(unsigned step=1;step<=frames;step++) {
            unsigned frame=(after+step)%frames;
            if(Uses(pixels+((size_t)frame*planes+axis)*width*height,(size_t)width*height,colour))return (int)frame;
        }
        return -1;
    }
};
