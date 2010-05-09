package examples.builtins;

import JyCSP.JavaCspChannel;

public class example3 {

	/**
	 *Example to show JavaCspChannels are blocking
	 */
	public static void main(String[] args) {
		JavaCspChannel c = new JavaCspChannel();
		c.read();

	}

}
