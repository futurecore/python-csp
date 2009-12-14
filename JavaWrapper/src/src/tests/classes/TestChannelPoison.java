package tests.classes;

import java.util.concurrent.Semaphore;

import JyCSP.*;
import org.python.core.PyString;

public class TestChannelPoison extends JavaCspProcess {

	public int y = 0;

	public JavaCspChannel chnl;

	public boolean tim = false;

	public boolean sleeptest = false;

	public boolean jointest = false;

	public TestChannelPoison() {
		super();
		this.chnl = new JavaCspChannel();
	}

	public void target() {
		this.chnl.poison();
	}

}
