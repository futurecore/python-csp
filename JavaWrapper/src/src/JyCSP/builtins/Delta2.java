package JyCSP.builtins;

import JyCSP.JavaCspChannel;
import JyCSP.JavaCspProcess;

public class Delta2 extends JavaCspProcess {
	private JavaCspChannel cin;

	private JavaCspChannel cout0;

	private JavaCspChannel cout1;

	public Delta2(JavaCspChannel cin, JavaCspChannel cout0, JavaCspChannel cout1) {
		super();
		this.cin = cin;
		this.cout0 = cout0;
		this.cout1 = cout1;
	}

	@Override
	public void target() {
		while (true) {
			Object val = this.cin.read();
			this.cout0.write(val);
			this.cout1.write(val);
		}
	}
}
