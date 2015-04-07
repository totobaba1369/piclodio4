#!/bin/bash

ps aux|grep [m]player
if [[ $? -ne 0 ]]; then
    mplayer $1
fi
