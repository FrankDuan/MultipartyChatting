# MultipartyChatting

This is a simple multiparty chatting application, which allows one or more 
members to send messages to other members simultaneously. Members can join and 
leave the conversation at any time. This system is based on peer to peer 
networking architecture. It does not need a central node. It implements 
multicast in the application layer based on TCP and does not depend on the 
multicast functionality of the network layer such as IGMP. 

The app can be run in two modes, GUI mode and command line mode.

1) GUI mode

python3 gui.py

2) Command line mode

python3 p2p_chatting.py {chairman_ip} {your name}

