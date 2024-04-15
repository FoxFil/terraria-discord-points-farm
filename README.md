# Terraria Discord AFK Points Farm
## ⚠️ Please note that using this script is against both the Terraria Discord rules and Discord ToS and may result in an account ban. ⚠️

This is a little Python script that is hard-coded to farm points in Terraria Discord (but with some programming skills you can modify it to work with any other servers).
So, what are the points? Basically this is a server's currency. Using points you can buy plenty of stuff from the shop.

<img src="https://github.com/FoxFil/terraria-discord-points-farm/assets/83007290/fc1d40c4-5085-4e47-bd4c-43dfa5afbdd8" width=400px>

### Ways to earn points 💰
#### 👑 Trivia
Every *5 minutes* Terraria Trivia question is sent in a special channel. If you answer first you get **100 points**.

<img src="https://github.com/FoxFil/terraria-discord-points-farm/assets/83007290/7fafb87e-cd5b-45ea-89f0-a80b191f9fb1" width=400px>

#### ⚔️ Epic Battle
Epic battles take place once *every hour*, starting on the *half-hour mark* (e.g. 1:30, 2:30, etc.). First, you need to register to the game using `bb!register` command. When the game starts, you will be asked *3 Terraria Trivia questions* in DMs with a bot. The person who answers the questions the fastest wins and gets **1000 points** (1st place).

<img src="https://github.com/FoxFil/terraria-discord-points-farm/assets/83007290/f08fe0e8-ad55-43e2-954e-1c38dce6645d" width=400px>

Now that we know how to earn points, let's automate the process! 😁

### Automation 🤖
#### 👑 Trivia
The autobot checks that the number of minutes is divided by 5 every 0.5 seconds. If so, the autobot reads the latest chat message from Trivia Bot and receives a question from it.
Afterwards, the autobot searches for this question in the chat, reads who answered the question correctly, then looks for a message from this person and sends it to the chat.
Here is a scheme that would help you understand how this works.

<img src="https://github.com/FoxFil/terraria-discord-points-farm/assets/83007290/d207f7bf-f433-4ddb-abab-6a4c8a0d36a6" width=1000px>

#### ⚔️ Epic Battle
Autobot selects a random time to register and registers for the game at that time.
Afterwards, the autobot waits when the number of minutes is 31 and verifies the participation by sending a message to the Game Bot.
Then, autobot reads the first question from DMs with the Game Bot. Next, using the same method as in Trivia, it searches for the answer to the question and sends it to the bot. This happens 3 times. I am also attaching a scheme for better understanding :)

<img src="https://github.com/FoxFil/terraria-discord-points-farm/assets/83007290/3442d9fc-a6ce-4e6b-97b6-8a26bc3e0c9d" width=1000px>


### Humanization 🧑
Now, let's make the autobot look like a real human. Here is what I did:
- 20% chance of not answering the question
- 0.05% chance of typo
- 20% chance of answer being capitalized and 80% of being lowered
- added typing requests
- added 0.15 seconds sleep for each symbol in an answer (so that it looks like the autobot is actually typing lol)

### Results 📝
With this autobot you can earn up to **1600 points / hour**. However, with current chances that I used for humanization, your income would approximately be from **900 to 1100 points / hour**.

Also, I do not recommend using the autobot more than 9 hours / day because it would definitely look suspicious if a person farms points for so long haha.

### Libraries required 📚
- [requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

### Creator 🧡
It's me, [FoxFil](https://github.com/FoxFil)! Enjoy your auto points hehe 😈
