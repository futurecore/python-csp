package tests.classes;

import java.util.concurrent.Semaphore;

import JyCSP.*;

import org.python.core.PyString;

public class TestSeqProcess extends JavaCspProcess {

	public int y = 0;
	private JavaCspChannel chnl;

	public TestSeqProcess(JavaCspChannel c,int y) {
		super();
		this.chnl = c;
		this.y = y;
	}

	public void target() {
		System.out.println(this.y);
		this.chnl.write(Integer.valueOf(this.y).toString());
	}

}
