package tests;

import tests.classes.TestSeqProcess;
import JyCSP.*;
import junit.framework.TestCase;

public class TestAlt extends TestCase {

	private Alt a ;
	private JavaCspChannel c0;
	private JavaCspChannel c1;
	private JavaCspChannel c2;
	private JavaCspChannel c3;
	private JavaCspChannel c4;
	private JavaCspChannel c5;
	private JavaCspChannel c6;
	private JavaCspChannel c[];
	
	
	public TestAlt(String name) {
		super(name);
	}

	protected void setUp() throws Exception {
		super.setUp();
		c0 = new JavaCspChannel();
		c1 = new JavaCspChannel();
		c2 = new JavaCspChannel();
		c3 = new JavaCspChannel();
		c4 = new JavaCspChannel();
		c5 = new JavaCspChannel();
		c6 = new JavaCspChannel();
		c = new JavaCspChannel[] {c0,c1,c2,c3,c4,c5,c6};
		
	}

	protected void tearDown() throws Exception {
		super.tearDown();
	}

	public void testAlt() {
		try{
			this.a = new Alt(c0,c1,c2,c3,c4,c5,c6);
		}catch (Exception e){
			assertTrue(false);
		}
	}

	public void testPoison() {
		fail("Not yet implemented");
	}

	public void testPri_select() {
		this.a = new Alt(c);
		TestSeqProcess sp = new TestSeqProcess(c);
		sp.start();
/*		try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}*/
		for (int i=0; i<this.c.length; i++) {
			assertTrue(this.a.pri_select() instanceof String);
		}
		
		
	}

	public void testSelect() {
		this.a = new Alt(c);
		TestSeqProcess sp = new TestSeqProcess(c);
		sp.start();
		try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		assertTrue(this.a.pri_select() instanceof String);
	}

	public void testFair_select() {
		this.a = new Alt(c);
		TestSeqProcess sp = new TestSeqProcess(c);
		sp.start();
		try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		assertTrue(this.a.pri_select() instanceof String);
	}

	public void testHasNext() {
		this.a = new Alt(c);
		TestSeqProcess sp = new TestSeqProcess(c);
		sp.start();
		try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		assertTrue(this.a.pri_select() instanceof String);
		assertTrue(this.a.hasNext());
	}

	public void testGetGuardLength() {
		this.a = new Alt(c);
		System.out.println(this.a.getGuardLength());
	}

}
