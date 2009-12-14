package JyCSP.builtins;

import JyCSP.*;

public class Generator extends JavaCspProcess {

	private JavaCspChannel cout;

	public Generator(JavaCspChannel cout) {
		super();
		this.cout = cout;

	}

	@Override
	public void target() {
		int count = 0;
		while (true) {
			this.cout.write(count);
			count++;
		}
	}
}
