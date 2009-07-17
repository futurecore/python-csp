package tests;

import JyCSP.Alt;
import JyCSP.JavaCspChannel;
import JyCSP.Seq;
import tests.classes.TestProcess;
import tests.classes.TestSeqProcess;
import junit.framework.TestCase;

public class TestSeq extends TestCase {

	TestSeqProcess t0;
	TestSeqProcess t1;
	TestSeqProcess t2;
	JavaCspChannel c0;
	JavaCspChannel c1;
	JavaCspChannel c2;
	Seq t;
	
	public TestSeq(String name) {
		super(name);
	}

	protected void setUp() throws Exception {
		super.setUp();
		c0 = new JavaCspChannel();
		c1 = new JavaCspChannel();
		c2 = new JavaCspChannel();

		t0 = new TestSeqProcess(c0,0);
		t1 = new TestSeqProcess(c1,1);
		t2 = new TestSeqProcess(c2,2);
	}

	protected void tearDown() throws Exception {
		super.tearDown();
	}

	public void testSeq() {
		try {

			this.t = new Seq(t0,t1,t2);
		} catch (Exception e) {
			e.printStackTrace();
			assertTrue(false);
		}
	}

	public void testStart() {
		this.t = new Seq(t0,t1,t2);
		this.t.start();
		Alt a = new Alt(c0,c1,c2);
		String a1 = (String) a.pri_select();
		String a2 = (String) a.pri_select();
		String a3 = (String) a.pri_select();
		assertEquals(a1, "0");
		assertEquals(a2, "1");
		assertEquals(a3, "2");
	}

}
