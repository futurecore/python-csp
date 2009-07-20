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
		SeqProcess t0 = new SeqProcess(this.chnl[0],0);
		SeqProcess t1 = new SeqProcess(this.chnl[1],1);
		SeqProcess t2 = new SeqProcess(this.chnl[2],2);
		
		new Seq(t0,t1,t2).start();
	}

}
