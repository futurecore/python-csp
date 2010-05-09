package JyCSP.builtins;

import JyCSP.*;

public class FixedDelay extends JavaCspProcess {

	private JavaCspChannel cin;
	
	private JavaCspChannel cout;

	private int res;

	public FixedDelay(JavaCspChannel cin,JavaCspChannel cout, int resolution) {
		super();
		this.cin = cin;
		this.cout = cout;
		this.res = resolution;

	}

	@Override
	public void target() {
		while (true) {
			try {
				Object val = this.cin.read();
				Thread.sleep(res);
				this.cout.write(val);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

		}
	}
}
