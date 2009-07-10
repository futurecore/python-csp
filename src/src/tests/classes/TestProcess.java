package tests.classes;

import java.util.concurrent.Semaphore;

import JyCSP.*;
import org.python.core.PyString;

public class TestProcess extends JavaCspProcess {

	public int y = 0;

	public JavaCspChannel chnl;

	public boolean tim = false;

	public boolean sleeptest = false;

	public boolean jointest = false;

	public TestProcess() {
		super();
		this.chnl = new JavaCspChannel();
	}

	public void target() {
		this.chnl.write("Hello World");

		if (jointest) {
			for (int i = 0; i < 1000; i++) {
				this.y++;

			}
			this.chnl.write(y);
		}

		while (sleeptest) {
			this.chnl.write(System.currentTimeMillis());
		}

		while (tim) {
		}
	}

}
