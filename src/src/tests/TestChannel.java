package tests;

import tests.classes.ChannelConsumer;
import tests.classes.TestChannelPoison;
import JyCSP.Alt;
import JyCSP.JavaCspChannel;
import junit.framework.TestCase;

public class TestChannel extends TestCase {
	
	JavaCspChannel chnl;

	protected void setUp() throws Exception {
		super.setUp();
		this.chnl = new JavaCspChannel();
	}

	protected void tearDown() throws Exception {
		super.tearDown();
		this.chnl = null;
	}

	public void testJavaCspChannel() {
		try{
			this.chnl = new JavaCspChannel();
		}catch (Exception e){
			assertTrue(false);
		}
		
		
	}

	public void testWrite() {
		ChannelConsumer cc = new ChannelConsumer(this.chnl);
		cc.start();
		String s = (String)this.chnl.read();
		assertEquals(s,"test");
	}

	public void testRead() {
		ChannelConsumer cc = new ChannelConsumer(this.chnl);
		cc.start();
		String s = (String)this.chnl.read();
		assertEquals(s,"test");
	}

	public void testPoison() {
		TestChannelPoison tc = new TestChannelPoison();
		tc.start();
	}

	public void testSelect() {
		ChannelConsumer cc = new ChannelConsumer(this.chnl);
		cc.start();
		Alt a = new Alt(this.chnl);
		String s = (String) a.select();
		assertEquals(s,"test");
	}

}
