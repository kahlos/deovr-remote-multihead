# deovr-remote-multihead
Controlling multiple headsets running DeoVR all at the same time

Python reimplementation of the C# reference at https://deovr.com/app/doc#remote-control

Using ChatGPT to rebuild the functionality and extend for use with multiple headsets.

Features:
* Control and monitor multiple headsets individually
* Simultaneous control of all headsets
* Syncronisation method with playback speed to find perfect sync

There's some bugs in the sync method causing the master headset to become unresponsive to commands. Disconnecting and reconnecting seems to be the solution for now!
