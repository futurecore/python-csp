package tests;

import JyCSP.Alt;
import JyCSP.JavaCspSkipGuard;
import JyCSP.Seq;
import junit.framework.TestCase;

public class TestSkipGuard extends TestCase {

	public TestSkipGuard(String name) {
		super(name);
	}

	protected void setUp() throws Exception {
		super.setUp();
	}

	protected void tearDown() throws Exception {
		super.tearDown();
	}

	public void testJavaCspSkipGuard() {
		try {

			new JavaCspSkipGuard();
		} catch (Exception e) {
			e.printStackTrace();
			assertTrue(false);
		}
	}
	
	public void testSkippingAlt(){
		JavaCspSkipGuard g = new JavaCspSkipGuard();
		Alt a = new Alt(g);
		a.select();
		
	}

}
