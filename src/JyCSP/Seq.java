package JyCSP;

import org.python.core.*;

/**
 * 
 * @author Sam Wilson, Sarah Mount
 * @version 1.0
 * 
 *  Java representation of the Jython Class Seq.
 * 
 * 
 * 
 */

public class Seq extends PyObject implements JyCspSeqInterface{
	
	/**
	 * Java Seq Interface for the Jython Class Seq.
	 */
	protected JyCspSeqInterface jcsi;
	
	/**
	 * Default constructor creates a Seq Object
	 * 
	 * Makes a static call to CspFactory method creatJavaCspSeq
	 * 
	 * @param args List of Processes
	 */
	public Seq(JavaCspProcess...args){
		super();
		this.jcsi = CspFactory.createJavaCspSeq(args);
	}

	/**
	 * Straight through method call to Seq.run()
	 * 
	 * UnKnown behaviour
	 */
	public void run() {
		this.jcsi.run();
	}

	/**
	 * Straight through method call to Seq.Start()
	 * 
	 * Starts the Seq
	 */
	public void start() {
		this.jcsi.start();
	}

	/**
	 * Straight through method call to Seq.Stop()
	 * Stops the Seq
	 * 
	 * Unknown behaviour
	 */
	public void stop() {
		this.jcsi.stop();
	}

}
