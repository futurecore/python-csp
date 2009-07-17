package tests.classes;

//import JyCSP.Alt;
import JyCSP.JavaCspChannel;

public class ChannelConsumer extends Thread {

	private JavaCspChannel chnl;
	
	private String rec;

	public ChannelConsumer(JavaCspChannel chnl) {
		this.chnl = chnl;
	}

	public void run() {
		this.chnl.write("test");
		//Alt a = new Alt(this.chnl);
		//while (running) {
			//String s = (String) a.select();
			//String s = (String) this.chnl.read();
			//System.out.println(s);
			//this.rec = s;
		//}
	}

	public String getRec() {
		return rec;
	}
}
