package tests;

import JyCSP.Alt;
import JyCSP.TimerGuard;
import tests.classes.TestProcess;
import junit.framework.TestCase;

public class TestTimerGuard extends TestCase {

	private TimerGuard t;

	public TestTimerGuard(String name) {
		super(name);
	}

	protected void setUp() throws Exception {
		super.setUp();
	}

	protected void tearDown() throws Exception {
		super.tearDown();
	}

	public void testTimerGuard() {
		try {
			this.t = new TimerGuard();
		} catch (Exception e) {
			assertTrue(false);
		}
	}

	public void testSleep() {
		TimerGuard guard = new TimerGuard();
        guard.setAlarm(5);
        Alt alt = new Alt(guard);
        long t0 = guard.read();
        alt.select();
        float duration = guard.read() - t0;
       assertEquals(duration, 5f, 1f);
  
	}
}
