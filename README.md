# accountsreceivable
A family friend has been running Accounts Receivable by SBT software for decades. His entire business depends on a WindowsXP machine. This repo is a modernized ground-up rewrite. 

I started by moving his database schema to sqlite3, since he doesn't need a full sql server.
Then I wrote a FastAPI to interface with the sqite3 db.
And finally, added a front-end.

Its a work in progress. Don't expect much.
-Ash
