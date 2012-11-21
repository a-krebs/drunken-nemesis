import math

class Vector2(object):
    """
    A 2d Vector class
    """

    def __init__(self, x, y):
        super(Vector2, self).__init__()
        self.x = float(x)
        """
        The x parameter
        """
        self.y = float(y)
        """
        The y parameter
        """

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __eq__(self, other):
        return other and isinstance(other, Vector2) and (self.x == other.x) and (self.y == other.y)

    def __ne__(self, other):
        return not other or not isinstance(other, Vector2) or (self.x != other.x) or (self.y != other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * float(other), self.y * float(other))
    def __rmul__(self, other):
        return Vector2(self.x * float(other), self.y * float(other))

    def __div__(self, other):
        return Vector2(self.x / float(other), self.y / float(other))

    def __pos__(self):
        return Vector2(self.x, self.y)

    def __neg__(self):
        return Vector2(-self.x, -self.y)


    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def squaredLength(self):
        return self.x * self.x + self.y * self.y

    def distance(self, other):
        return (other - self).length()

    def squaredDistance(self, other):
        return (other - self).squaredLength()

    def dotProduct(self, other):
        return self.x * other.x + self.y * other.y

    def normalize(self):
        d = self.length();
        assert d != 0
        self.x /= d
        self.y /= d

    def normalized(self):
        d = self.length();
        assert d != 0
        return self / d

    def midPoint(self, other):
        return 0.5 * (self + other)

    # def makeFloor(self):
    # return math.sqrt(self.x * self.x + self.y * self.y)

    # def makeCeil(self):
    # return math.sqrt(self.x * self.x + self.y * self.y)

    def perpendicular(self):
        return Vector2(-self.y, self.x)

    def crossProduct(self, other):
        return self.x * other.y - self.y * other.x;

    # def randomDeviant(self):
    # return math.sqrt(self.x * self.x + self.y * self.y)

    def isZeroLength(self):
        return self.squaredLength() < 0.001

    # def reflect(self, normal):
    # """
    # Calculates a reflection vector to the plane with the given normal.
    # """
        # return Vector2(self - (2 * self.dotProduct(normal) * normal))



Vector2.ZERO = Vector2(0.0, 0.0)
Vector2.UNIT_X = Vector2(1.0, 0.0)
Vector2.UNIT_Y = Vector2(0.0, 1.0)
Vector2.NEGATIVE_UNIT_X = Vector2(-1.0, 0.0)
Vector2.NEGATIVE_UNIT_Y = Vector2(0.0, -1.0)
Vector2.UNIT_SCALE = Vector2(1.0, 1.0)

