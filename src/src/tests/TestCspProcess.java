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
		String str = (String) this.t.chnl.read();
		while (this.t.getState() != Thread.State.TERMINATED) {

		}
		assertTrue(str instanceof String);
	}

	public void testGetPid() {
		Object o = this.t.getPid();
		System.out.println(o);
		assertTrue(o instanceof Long);

	}

}