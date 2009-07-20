package tests;

import JyCSP.Alt;
import JyCSP.JavaCspChannel;
import JyCSP.TimerGuard;
import tests.classes.TestProcess;
import junit.framework.TestCase;

public class TestTimerGuard extends TestCase  {

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
			e.printStackTrace();
			assertTrue(false);
		}
	}

	public void testSleep() {
		TimerGuard guard = new TimerGuard();
        long t0 = guard.read();
        guard.sleep(5);
        float duration = guard.read() - t0;
        System.out.println("testSleep Duration: " + duration/1000);
        assertEquals(5, duration/1000, 1f); 
	}
	
	public void testSetAlarm() {
		TimerGuard guard = new TimerGuard();
	    guard.set_alarm(5); // 5 seconds

	    
        Alt alt = new Alt(guard);
        long t0 = guard.read();
        alt.select();
        float duration = guard.read() - t0;
        System.out.println("testSetAlarm Duration: " + duration/1000);
        assertEquals(5, duration/1000, 1f); // 5 seconds
  
	}
}
