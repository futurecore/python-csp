package JyCSP.builtins;

import java.io.PrintStream;

import JyCSP.*;

public class Printer extends JavaCspProcess {

	private JavaCspChannel cin;

	private PrintStream out;

	public Printer(JavaCspChannel cin, PrintStream o) {
		super();
		this.cin = cin;
		this.out = o;
	}

	public Printer(JavaCspChannel cin) {
		super();
		this.cin = cin;
		this.out = System.out;
	}

	@Override
	public void target() {
		while (true) {
			String s = this.cin.read().toString();
			this.out.println(s);
		}
	}
}
