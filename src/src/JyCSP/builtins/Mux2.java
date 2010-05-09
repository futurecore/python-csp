package JyCSP.builtins;

import JyCSP.Alt;
import JyCSP.JavaCspChannel;
import JyCSP.JavaCspProcess;

public class Mux2 extends JavaCspProcess {
	
	private JavaCspChannel cin0;

	private JavaCspChannel cin1;

	private JavaCspChannel cout;

	public Mux2(JavaCspChannel cin0, JavaCspChannel cin1, JavaCspChannel cout) {
		super();
		this.cin0 = cin0;
		this.cin1 = cin1;
		this.cout = cout;
	}

	@Override
	public void target() {
		Alt a = new Alt(this.cin0,this.cin1);
		while (true) {
			Object val = a.pri_select();
			this.cout.write(val);
		}
	}
}
