package tests;

import JyCSP.Alt;
import JyCSP.JavaCspChannel;
import JyCSP.Par;
import JyCSP.Seq;
import JyCSP.builtins.Blackhole;
import tests.classes.SeqProcess;
import tests.classes.TestProcess;
import tests.classes.TestSeqProcess;
import junit.framework.TestCase;

public class TestSeq extends TestCase {

	SeqProcess t0;
	SeqProcess t1;
	SeqProcess t2;
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

		t0 = new SeqProcess(c0,0);
		t1 = new SeqProcess(c1,1);
		t2 = new SeqProcess(c2,2);
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
		JavaCspChannel[] h = {c0,c1,c2};
		TestSeqProcess sp = new TestSeqProcess(h);
		sp.start();
		Alt a = new Alt(c0,c1,c2);
		String a1 = (String) c0.read();
		String a2 = (String) c1.read();
		String a3 = (String) c2.read();
		assertEquals(a1, "0");
		assertEquals(a2, "1");
		assertEquals(a3, "2");
	}

}
