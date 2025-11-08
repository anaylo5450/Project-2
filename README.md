COSC 635 Project 2 – Error Control (3-Week Plan)
Goal: Implement Stop-and-Wait (SAW) and Go-Back-N (GBN) protocols over UDP with simulated packet loss. The plan assumes three members with moderate programming experience and evenly distributes both programming and organizational work.
Team Roles (Equal Programming Distribution)
Member A	Member B	Member C
• SAW Sender developer
• Drafts protocol design
• Helps test & document
• Leads GitHub repo setup	• SAW Receiver + GBN Sender developer
• Adds window & ACK logic
• Co-writes weekly reports
• Tests across machines	• GBN Receiver developer
• Builds loss simulation + stats module
• Tests data integrity & records demo videos
• Final documentation & packaging
Timeline
WEEK 1 – Design & Setup (Nov 7–13)
• Agree on programming language 
• Define header fields, payload size, and sequence number rules
• A: Create protocol design document
• B: Build simple UDP send/receive test
• C: Prepare test file and verify file I/O
Deliverable: Protocol design + UDP test working between two machines

WEEK 2 – Stop-and-Wait Implementation (Nov 14–20)
• A: Implement SAW sender logic (send, wait, retransmit)
• B: Implement SAW receiver logic (ACK valid packets)
• C: Add random loss simulation and track stats
• All: Test with 2%, 5%, and 20% loss; verify received file
Deliverable: Working SAW + demo videos

WEEK 3 – Go-Back-N Implementation & Final Submission (Nov 21–27)
• A: Adapt SAW sender into GBN sender (window size)
• B: Implement GBN receiver with cumulative ACKs
• C: Integrate timing/statistics, verify file correctness
• All: Record GBN demo videos, finalize README, and zip all materials
Deliverable: Working GBN, all demo videos, final ZIP package

