## Running Engibot:
### Docker:
`docker build . -t engibot:latest`
`docker run --env-file .env -p 6934:6934 engibot`
You will need to have a MariaDB database for engibot to work! I use a docker container but that is up to you.
You may use [tables.sql](./sql/tables.sql) to make your own database with the supported tables.

## ENV Variables (tokens marked with * are necessary):
see the [template env](./env.template) for reference, make sure you name your production .env to `.env` with no prefix or suffix.
### DISCORD_TOKEN*
Discord Bot Token
### OPENAI_API_KEY*
URL For OPENAI services
### MARIADB_HOSTDB*
MariaDB Host and DB Name... must follow the format: **host|db**
Example: *192.168.68.99:3306|engibot*
### MARIADB_USER*
MariaDB User and Password... must follow the format: **username|password**
Example: *discordbot|securepassword*
### NTFY
Notification Service... must follow the format: **host|topic**
Example: *ntfy.domain.net|engibot*
### BOT_NAME*
Name of the bot
### BOT_STATUS*
Text status for the bot
### BOT_PREFIX*
Prefix for text commands
### BACKEND_HOST*
Host IP for the backend, can be 0.0.0.0
### BACKEND_PORT
Host Port for the backend, should be 6934 unless you edit /html/frontend.js and the Dockerfile
### MAX_MESSAGE_LENGTH
Used to cut bot messages into blocks to avoid sending messages past Discord's message length limit