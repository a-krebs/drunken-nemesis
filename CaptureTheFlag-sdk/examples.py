import random

from api import Commander
from api import commands
from api.vector2 import Vector2


def contains(area, position):
    start, finish = area
    return position.x >= start.x and position.y >= start.y and position.x <= finish.x and position.y <= finish.y


class RandomCommander(Commander):
    """
    Sends everyone to randomized positions or a random choice of flag location.  The behavior of returning the flag
    to the home base after capturing it is purely emergent!
    """

    def tick(self):
        """Process all the bots that are done with their orders and available for taking commands."""

        # The 'bots_available' list is a dynamically calculated list of bots that are done with their commands.
        for bot in self.game.bots_available:
            # Determine a place to run randomly...
            target = random.choice(
                          # 1) Either a random choice of *current* flag locations, ours or theirs.
                          [f.position for f in self.game.flags.values()]
                          # 2) Or a random choice of the goal locations for returning flags.
                        + [s for s in self.level.flagScoreLocations.values()]
                          # 3) Or a random position in the entire level, one that's not blocked.
                        + [self.level.findRandomFreePositionInBox(self.level.area)]
            )
            # Pick random movement style between going fast or moving carefully.
            commandType = random.choice([commands.Attack, commands.Charge])
            if target:
                self.issue(commandType, bot, target, description = 'random')


class GreedyCommander(Commander):
    """
    Always sends everyone to the flag of the enemy and the guy carrying the flag back again
    """

    def captured(self):
        """Did this team cature the enemy flag?"""
        return self.game.enemyTeam.flag.carrier != None

    def tick(self):
        """Process the bots that are waiting for orders, either send them all to attack or all to defend."""
        captured = self.captured()

        our_flag = self.game.team.flag.position
        their_flag = self.game.enemyTeam.flag.position
        their_base = self.level.botSpawnAreas[self.game.enemyTeam.name][0]

        # Only process bots that are done with their orders...
        for bot in self.game.bots_available:

            # If this team has captured the flag, then tell this bot...
            if captured:
                target = self.game.team.flagScoreLocation
                # 1) Either run home, if this bot is the carrier or otherwise randomly.
                if bot.flag is not None or (random.choice([True, False]) and (target - bot.position).length() > 8.0):
                    self.issue(commands.Charge, bot, target, description = 'scrambling home')
                # 2) Run to the exact flag location, effectively escorting the carrier.
                else:
                    self.issue(commands.Attack, bot, self.game.enemyTeam.flag.position, description = 'defending flag carrier',
                               lookAt = random.choice([their_flag, our_flag, their_flag, their_base]))

            # In this case, the flag has not been captured yet so have this bot attack it!
            else:
                path = [self.game.enemyTeam.flag.position]
                if contains(self.level.botSpawnAreas[self.game.team.name], bot.position) and random.choice([True, False]):
                    path.insert(0, self.game.team.flagScoreLocation)
                self.issue(commands.Attack, bot, path, description = 'attacking enemy flag',
                                lookAt = random.choice([their_flag, our_flag, their_flag, their_base]))


class DefenderCommander(Commander):
    """
    Leaves everyone to defend the flag except for one lone guy to grab the other team's flag.
    """

    def initialize(self):
        self.attacker = None

    def tick(self):
        # TODO: When defender is down to the last bot that's attacking the flag, it'll end up ordering
        # the attacker to run all the way back from the flag to defend!
        if self.attacker and self.attacker.health <= 0:
            self.attacker = None

        for bot in self.game.bots_available:
            if (not self.attacker or self.attacker == bot) and len(self.game.bots_available) > 1:
                self.attacker = bot

                if bot.flag:
                    #bring it hooome
                    targetLocation = self.game.team.flagScoreLocation
                    self.issue(commands.Charge, bot, targetLocation, description = 'returning enemy flag!')

                else:
                    # find the closest flag that isn't ours
                    enemyFlagLocation = self.game.enemyTeam.flag.position
                    self.issue(commands.Charge, bot, enemyFlagLocation, description = 'getting enemy flag!')

            else:
                if self.attacker == bot:
                    self.attacker = None

                # defend the flag!
                targetPosition = self.game.team.flagScoreLocation
                targetMin = targetPosition - Vector2(8.0, 8.0)
                targetMax = targetPosition + Vector2(8.0, 8.0)
                if bot.flag:
                    #bring it hooome
                    targetLocation = self.game.team.flagScoreLocation
                    self.issue(commands.Charge, bot, targetLocation, description = 'returning enemy flag!')
                else:
                    if (targetPosition - bot.position).length() > 9.0 and  (targetPosition - bot.position).length() > 3.0 :
                        while True:
                            position = self.level.findRandomFreePositionInBox((targetMin,targetMax))
                            if position and (targetPosition - position).length() > 3.0:
                                self.issue(commands.Move, bot, position, description = 'defending around flag')
                                break
                    else:
                        self.issue(commands.Defend, bot, (targetPosition - bot.position), description = 'defending facing flag')


class BalancedCommander(Commander):
    """An example commander that has one bot attacking, one defending and the rest randomly searching the level for enemies"""

    def initialize(self):
        self.attacker = None
        self.defender = None
        self.verbose = False

        # Calculate flag positions and store the middle.
        ours = self.game.team.flag.position
        theirs = self.game.enemyTeam.flag.position
        self.middle = (theirs + ours) / 2.0

        # Now figure out the flaking directions, assumed perpendicular.
        d = (ours - theirs)
        self.left = Vector2(-d.y, d.x).normalized()
        self.right = Vector2(d.y, -d.x).normalized()
        self.front = Vector2(d.x, d.y).normalized()


    # Add the tick function, called each update
    # This is where you can do any logic and issue new orders.
    def tick(self):

        if self.attacker and self.attacker.health <= 0:
            # the attacker is dead we'll pick another when available
            self.attacker = None

        if self.defender and (self.defender.health <= 0 or self.defender.flag):
            # the defender is dead we'll pick another when available
            self.defender = None

        # In this example we loop through all living bots without orders (self.game.bots_available)
        # All other bots will wander randomly
        for bot in self.game.bots_available:           
            if (self.defender == None or self.defender == bot) and not bot.flag:
                self.defender = bot

                # Stand on a random position in a box of 4m around the flag.
                targetPosition = self.game.team.flagScoreLocation
                targetMin = targetPosition - Vector2(2.0, 2.0)
                targetMax = targetPosition + Vector2(2.0, 2.0)
                goal = self.level.findRandomFreePositionInBox([targetMin, targetMax])
                
                if (goal - bot.position).length() > 8.0:
                    self.issue(commands.Charge, self.defender, goal, description = 'running to defend')
                else:
                    self.issue(commands.Defend, self.defender, (self.middle - bot.position), description = 'turning to defend')

            elif self.attacker == None or self.attacker == bot or bot.flag:
                # Our attacking bot
                self.attacker = bot

                if bot.flag:
                    # Tell the flag carrier to run home!
                    target = self.game.team.flagScoreLocation
                    self.issue(commands.Move, bot, target, description = 'running home')
                else:
                    target = self.game.enemyTeam.flag.position
                    flank = self.getFlankingPosition(bot, target)
                    if (target - flank).length() > (bot.position - target).length():
                        self.issue(commands.Attack, bot, target, description = 'attack from flank', lookAt=target)
                    else:
                        flank = self.level.findNearestFreePosition(flank)
                        self.issue(commands.Move, bot, flank, description = 'running to flank')

            else:
                # All our other (random) bots

                # pick a random position in the level to move to                               
                halfBox = 0.4 * min(self.level.width, self.level.height) * Vector2(1, 1)
                
                target = self.level.findRandomFreePositionInBox((self.middle + halfBox, self.middle - halfBox))

                # issue the order
                if target:
                    self.issue(commands.Attack, bot, target, description = 'random patrol')

    def getFlankingPosition(self, bot, target):
        flanks = [target + f * 16.0 for f in [self.left, self.right]]
        options = map(lambda f: self.level.findNearestFreePosition(f), flanks)
        return sorted(options, key = lambda p: (bot.position - p).length())[0]
