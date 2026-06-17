# [ADOFAI](https://7thbe.at/#adofai) Level Compressor

~~isn't the title already enough to explain what is this for for you?~~

Notes that this tool only focuses on compressing `*.adofai` file using strategy that only works for ADOFAI level format. 

ADOFAI Updates may cause this to update, or even give up some compressing method.  
More specifically, this project is assuming that: 
* ADOFAI will not change default values for all events, decorations, and level settings frequently; 
* ADOFAI will fill the missing keys using default values when loading a level, if possible; 
* ADOFAI will not give up to support loading `pathData`-formatted levels. 

The current version of this project supports to compress levels from ADOFAI versions until `v3.1.2`. 

## [LICENSE](./LICENSE.md)

This repository includes some source code from the following projects:
* https://github.com/M1n3c4rt/adofaipy ([MIT License](https://opensource.org/licenses/MIT))