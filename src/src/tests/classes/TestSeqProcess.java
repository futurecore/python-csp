package tests.classes;

import java.util.concurrent.Semaphore;

import JyCSP.*;

import org.python.core.PyString;

public class TestSeqProcess extends Thread{

	public int y = 0;
	private JavaCspChannel chnl[];

	public TestSeqProcess(JavaCspChannel[] c) {
		super();
		this.chnl = c;
		this.y = y;
	}

	public void run() {
		SeqProcess[] t = new SeqProcess[this.chnl.length];
		for(int i = 0; i<this.chnl.length; i++){
			t[i] = new SeqProcess(this.chnl[i],i);
		}
		new Par(t).start();
	}

}
