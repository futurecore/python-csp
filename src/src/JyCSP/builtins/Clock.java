package JyCSP.builtins;

import JyCSP.*;

public class Clock extends JavaCspProcess {

	private JavaCspChannel cout;

	private int res;

	public Clock(JavaCspChannel cout, int resolution) {
		super();
		this.cout = cout;
		this.res = resolution;

	}

	@Override
	public void target() {
		while (true) {
			try {
				Thread.sleep(res);
				this.cout.write(new Object());
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}

		}
	}
}
