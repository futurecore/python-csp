package tests;

import java.math.BigInteger;

import tests.classes.TestProcess;
import junit.framework.TestCase;

public class TestCspProcess extends TestCase {

	TestProcess t;

	public TestCspProcess(String name) {
		super(name);
	}

	protected void setUp() throws Exception {
		super.setUp();
		this.t = new TestProcess();
	}

	protected void tearDown() throws Exception {
		super.tearDown();
	}

	public void testJavaCspProcess() {
		try {
			this.t = new TestProcess();
		} catch (Exception e) {
			assertTrue(false);
		}
	}

	public void testStart() {

		this.t.start();
		while (this.t.getState() != Thread.State.TERMINATED) {

		}
		assertTrue(this.t.chnl.read() instanceof String);
	}

	public void testRun() {
		this.t.run();
		assertTrue(this.t.chnl.read() instanceof String);
	}

	public void testSleep() {
		this.t.sleeptest = true;
		this.t.start();
		this.t.chnl.read();
		this.t.chnl.read();
		long t0 = ((BigInteger) t.chnl.read()).longValue();
		t.sleep(5);
		long t1 = ((BigInteger) t.chnl.read()).longValue();
		assertTrue(t1-t0 < 100);
	}

	public void testGetPid() {
		Object o = this.t.getPid();
		System.out.println(o);
		assertTrue(o instanceof Long);

	}

}
