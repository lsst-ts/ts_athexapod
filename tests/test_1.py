from lsst.ts import ATHexapod
import time
import unittest
from random import randint


class TestAtHexapod(unittest.TestCase):

    def setUp(self):
        self.hexController = ATHexapod.ATHexapodController()
        self.hexController.configureCommunicator(address='192.168.122.1', port=50000, connectTimeout=2,
                                                 readTimeout=2, sendTimeout=2, endStr='\n', maxLength=1024)
        self.hexController.connect()
        self.hexController.initializePosition()
        self.maxPosition = 4

    def tearDown(self):
        self.hexController.disconnect()

    # @unittest.skip("Takes to long to execute...")
    def testTarget(self):
        """Send target to the hexapod and test if it's the same as
        the hardware target."""
        Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd = 0, 0, 0, 0, 0, 0
        self.hexController.moveToPosition(Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd)

        for i in range(120):
            if(inPosition(self.hexController, Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd)):
                Xtgt, Ytgt, Ztgt, Utgt, Vtgt, Wtgt = self.hexController.getRealPositions()
                break
            time.sleep(1)

        self.assertEqual(Xcmd, Xtgt)
        self.assertEqual(Ycmd, Ytgt)
        self.assertEqual(Zcmd, Ztgt)
        self.assertEqual(Ucmd, Utgt)
        self.assertEqual(Vcmd, Vtgt)
        self.assertEqual(Wcmd, Wtgt)

    @unittest.skip("Didn't work on the simulator, not sure if will work on the real controller")
    def testReasyStatus(self):
        """Send random target and wait until reasyStatus is true."""
        Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd = (randint(0, self.maxPosition) for i in range(6))
        self.hexController.moveToPosition(Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd)

        for i in range(120):
            ready = self.hexController.getReadyStatus()
            if(ready):
                Xtgt, Ytgt, Ztgt, Utgt, Vtgt, Wtgt = self.hexController.getRealPositions()
                break
            time.sleep(1)

        self.assertEqual(Xcmd, Xtgt)
        self.assertEqual(Ycmd, Ytgt)
        self.assertEqual(Zcmd, Ztgt)
        self.assertEqual(Ucmd, Utgt)
        self.assertEqual(Vcmd, Vtgt)
        self.assertEqual(Wcmd, Wtgt)

    # @unittest.skip("Takes to long to execute...")
    def testMoveToTarget(self):
        """Send target to the hexapod and test if it's the same as
        the hardware target.
        """

        Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd = (randint(0, self.maxPosition) for i in range(6))
        self.hexController.moveToPosition(Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd)
        for i in range(120):
            # Break if position has been reached
            if(inPosition(self.hexController, Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd)):
                Xtgt, Ytgt, Ztgt, Utgt, Vtgt, Wtgt = self.hexController.getRealPositions()
                break
            time.sleep(1)

        self.assertAlmostEqual(Xcmd, Xtgt, places=3)
        self.assertAlmostEqual(Ycmd, Ytgt, places=3)
        self.assertAlmostEqual(Zcmd, Ztgt, places=3)
        self.assertAlmostEqual(Ucmd, Utgt, places=3)
        self.assertAlmostEqual(Vcmd, Vtgt, places=3)
        self.assertAlmostEqual(Wcmd, Wtgt, places=3)

    @unittest.skip("Didn't work on the simulator, not sure if will work on the real controller")
    def testMotionStatus(self):
        """Send random target and test if the onTarget is True
        when the Hexapod has reached position.
        """
        Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd = (randint(0, self.maxPosition) for i in range(6))
        self.hexController.moveToPosition(Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd)
        for i in range(120):
            XonTarget, YonTarget, ZonTarget, UonTarget, VonTarget, WonTarget = \
                self.hexController.getOnTargetState()
            onTarget = XonTarget and YonTarget and ZonTarget and UonTarget and VonTarget and WonTarget
            print(onTarget)
            if(onTarget):
                break
            time.sleep(1)

        self.assertTrue(onTarget)

    def testLowLimits(self):
        """Test setting up low limits."""
        Xlow, Ylow, Zlow, Ulow, Vlow, Wlow = 0, 0, 0, 0, 0, 0
        self.hexController.setPositionLimits(minPositionX=Xlow, minPositionY=Ylow, minPositionZ=Zlow,
                                             minPositionU=Ulow, minPositionV=Vlow, minPositionW=Wlow)
        XlowTgt, YlowTgt, ZlowTgt, UlowTgt, VlowTgt, WlowTgt = self.hexController.getLowLimits()

        self.assertAlmostEqual(Xlow, XlowTgt, places=3)
        self.assertAlmostEqual(Ylow, YlowTgt, places=3)
        self.assertAlmostEqual(Zlow, ZlowTgt, places=3)
        self.assertAlmostEqual(Ulow, UlowTgt, places=3)
        self.assertAlmostEqual(Vlow, VlowTgt, places=3)
        self.assertAlmostEqual(Wlow, WlowTgt, places=3)

        Xlow, Ylow, Zlow, Ulow, Vlow, Wlow = -22.5, -22.5, -12.5, -7.5, -7.5, -12.5
        self.hexController.setPositionLimits(minPositionX=Xlow, minPositionY=Ylow, minPositionZ=Zlow,
                                             minPositionU=Ulow, minPositionV=Vlow, minPositionW=Wlow)
        XlowTgt, YlowTgt, ZlowTgt, UlowTgt, VlowTgt, WlowTgt = self.hexController.getLowLimits()

        self.assertAlmostEqual(Xlow, XlowTgt, places=3)
        self.assertAlmostEqual(Ylow, YlowTgt, places=3)
        self.assertAlmostEqual(Zlow, ZlowTgt, places=3)
        self.assertAlmostEqual(Ulow, UlowTgt, places=3)
        self.assertAlmostEqual(Vlow, VlowTgt, places=3)
        self.assertAlmostEqual(Wlow, WlowTgt, places=3)

    def testHighLimits(self):
        """Test setting up high limits."""
        Xhigh, Yhigh, Zhigh, Uhigh, Vhigh, Whigh = 0, 0, 0, 0, 0, 0
        self.hexController.setPositionLimits(maxPositionX=Xhigh, maxPositionY=Yhigh, maxPositionZ=Zhigh,
                                             maxPositionU=Uhigh, maxPositionV=Vhigh, maxPositionW=Whigh)
        XhighTgt, YhighTgt, ZhighTgt, UhighTgt, VhighTgt, WhighTgt = self.hexController.getHighLimits()

        self.assertAlmostEqual(Xhigh, XhighTgt, places=3)
        self.assertAlmostEqual(Yhigh, YhighTgt, places=3)
        self.assertAlmostEqual(Zhigh, ZhighTgt, places=3)
        self.assertAlmostEqual(Uhigh, UhighTgt, places=3)
        self.assertAlmostEqual(Vhigh, VhighTgt, places=3)
        self.assertAlmostEqual(Whigh, WhighTgt, places=3)

        Xhigh, Yhigh, Zhigh, Uhigh, Vhigh, Whigh = 22.5, 22.5, 12.5, 7.5, 7.5, 12.5
        self.hexController.setPositionLimits(maxPositionX=Xhigh, maxPositionY=Yhigh, maxPositionZ=Zhigh,
                                             maxPositionU=Uhigh, maxPositionV=Vhigh, maxPositionW=Whigh)
        XhighTgt, YhighTgt, ZhighTgt, UhighTgt, VhighTgt, WhighTgt = self.hexController.getHighLimits()

        self.assertAlmostEqual(Xhigh, XhighTgt, places=3)
        self.assertAlmostEqual(Yhigh, YhighTgt, places=3)
        self.assertAlmostEqual(Zhigh, ZhighTgt, places=3)
        self.assertAlmostEqual(Uhigh, UhighTgt, places=3)
        self.assertAlmostEqual(Vhigh, VhighTgt, places=3)
        self.assertAlmostEqual(Whigh, WhighTgt, places=3)

    def testPositionUnit(self):
        xunit, yunit, zunit, uunit, vunit, wunit = self.hexController.getUnits()
        self.assertEqual(xunit.strip(), "mm")
        self.assertEqual(yunit.strip(), "mm")
        self.assertEqual(zunit.strip(), "mm")
        self.assertEqual(uunit.strip(), "deg")
        self.assertEqual(vunit.strip(), "deg")
        self.assertEqual(wunit.strip(), "deg")

    def testStop(self):
        """Send move command, then stop and compare current positions."""
        Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd = (randint(0, self.maxPosition) for i in range(6))
        self.hexController.moveToPosition(Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd)

        time.sleep(1)
        self.hexController.stopMotion()
        time.sleep(2)
        Xtgt1, Ytgt1, Ztgt1, Utgt1, Vtgt1, Wtgt1 = self.hexController.getRealPositions()
        time.sleep(1)
        Xtgt2, Ytgt2, Ztgt2, Utgt2, Vtgt2, Wtgt2 = self.hexController.getRealPositions()

        self.assertAlmostEqual(Xtgt1, Xtgt2, places=3)
        self.assertAlmostEqual(Ytgt1, Ytgt2, places=3)
        self.assertAlmostEqual(Ztgt1, Ztgt2, places=3)
        self.assertAlmostEqual(Utgt1, Utgt2, places=3)
        self.assertAlmostEqual(Vtgt1, Vtgt2, places=3)
        self.assertAlmostEqual(Wtgt1, Wtgt2, places=3)

    # @unittest.skip("Takes to long to execute...")
    def testOffsetMove(self):
        """Send move offset and compare positions to where it should be."""
        offsetX, offsetY, offsetZ, offsetU, offsetV, offsetW = 1.5, 1.5, 1.5, 1.5, 1.5, 1.5
        Xtgt, Ytgt, Ztgt, Utgt, Vtgt, Wtgt = self.hexController.getRealPositions()

        self.hexController.moveOffset(offsetX, offsetY, offsetZ, offsetU, offsetV, offsetW)

        for i in range(120):
            if inPosition(self.hexController, Xtgt+offsetX, Ytgt+offsetY, Ztgt+offsetZ,
                          Utgt+offsetU, Vtgt+offsetV, Wtgt+offsetW):
                Xtgt1, Ytgt1, Ztgt1, Utgt1, Vtgt1, Wtgt1 = self.hexController.getRealPositions()
                break
            time.sleep(1)

        self.assertEqual(Xtgt+offsetX, Xtgt1)
        self.assertEqual(Ytgt+offsetY, Ytgt1)
        self.assertEqual(Ztgt+offsetZ, Ztgt1)
        self.assertEqual(Utgt+offsetU, Utgt1)
        self.assertEqual(Vtgt+offsetV, Vtgt1)
        self.assertEqual(Wtgt+offsetW, Wtgt1)

    def testGetErrors(self):
        """Get error list."""
        errors = self.hexController.getErrors()
        print(errors)

    def testSetPivot(self):
        """Test set pivot."""
        self.hexController.setPivot(3, 3, 3)
        pivotX, pivotY, pivotZ = self.hexController.getPivot()
        self.assertEqual(pivotX, 3)
        self.assertEqual(pivotY, 3)
        self.assertEqual(pivotZ, 3)

        self.hexController.setPivot(0, 0, 0)
        pivotX, pivotY, pivotZ = self.hexController.getPivot()
        self.assertEqual(pivotX, 0)
        self.assertEqual(pivotY, 0)
        self.assertEqual(pivotZ, 0)

    def testSoftLimitsStatus(self):
        """Test set sft limits status."""
        xb, yb, zb, ub, vb, wb = False, False, False, False, False, False
        self.hexController.setSoftLimitStatus(X=xb, Y=yb, Z=zb, U=ub, V=vb, W=wb)
        x, y, z, u, v, w = self.hexController.getSoftLimitStatus()
        self.assertEqual(xb, x)
        self.assertEqual(yb, y)
        self.assertEqual(zb, z)
        self.assertEqual(ub, u)
        self.assertEqual(vb, v)
        self.assertEqual(wb, w)

        xb, yb, zb, ub, vb, wb = True, True, True, True, True, True
        self.hexController.setSoftLimitStatus(X=xb, Y=yb, Z=zb, U=ub, V=vb, W=wb)
        x, y, z, u, v, w = self.hexController.getSoftLimitStatus()
        self.assertEqual(xb, x)
        self.assertEqual(yb, y)
        self.assertEqual(zb, z)
        self.assertEqual(ub, u)
        self.assertEqual(vb, v)
        self.assertEqual(wb, w)

    def testVirtualMove(self):
        """Test virtual move."""
        valid = self.hexController.validPosition(X=50)
        self.assertEqual(valid, False)

        valid = self.hexController.validPosition(X=5)
        self.assertEqual(valid, True)

        valid = self.hexController.validPosition(X=5, Y=1, Z=1)
        self.assertEqual(valid, True)

        valid = self.hexController.validPosition(X=5, Y=1, Z=1, U=35)
        self.assertEqual(valid, False)


def similarTo(number1, number2, threshold=0.001):
    return abs(number1-number2) < threshold


def inPosition(hexController, Xcmd, Ycmd, Zcmd, Ucmd, Vcmd, Wcmd):
    Xtgt, Ytgt, Ztgt, Utgt, Vtgt, Wtgt = hexController.getRealPositions()
    inPosition = (similarTo(Xcmd, Xtgt) and similarTo(Ycmd, Ytgt) and similarTo(Zcmd, Ztgt) and
                  similarTo(Ucmd, Utgt) and similarTo(Vcmd, Vtgt) and similarTo(Wcmd, Wtgt))
    return inPosition


if __name__ == '__main__':
    atHexTests = unittest.main()
