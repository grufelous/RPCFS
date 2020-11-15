# RPCFS

## How to Install

1. Install `cryptography`:
  
    `pip instal cryptography`
  
    or
  
    `conda install cryptography`

2. Start the coordinator, followed by fs, and then finally the client

## Running

1. Start the coordinator process:
  
    `python coordinator.py`

2. Start the file servers:
  
    By default, we use ports starting from 7000 for ease. You can supply a new port as a command line argument. If not supplied, new FS will linearly probe from 7000 and work till the next 10 ports. If more FS are needed, refer the current limitations section.
  
    `python fs.py 7000`
  
    `python fs.py 7001`
  
    `python fs.py 7002`

3. Start the client processes:
  
    We can have upto 10 clients (refer current limitations). The clients are ordered by command line arguments to effectively use the saved demo keys.
  
    `python client.py`
  
    or
  
    `python client.py 0`
  
    `python client.py 1`

4. Send commands:
  
    Folders are automatically created with a prefix `fs_`. Just add files into these folders and explore through the client processes. Make sure you have enough permissions to do the same.

## Current Limitations

1. Limited keys
  
    Each FS and client needs to be registered with the coordinator to implement the Needham–Schroeder protocol. I have saved 10 keys for each for the time being. More can be created by letting the FS and client append to these files. However, for the purpose of demonstration, 10 is a very good limit. The coordinator uses modular arithmetic to read these keys and assign them to connecting processes.

2. No write operations
  
    This project started as an innovative project for the course CO407 (Distributed Systems), and that did not require any write RPC operations. The only write instruction it does is copy an existing file into a new one. To avoid feature creep before grading of the project, more instructions were not included. However, more write instructions can be considered for future releases.

3. No copying across file servers
  
    This is another feature not required for submission as an innovative project for CO407. It can be included in future releases.