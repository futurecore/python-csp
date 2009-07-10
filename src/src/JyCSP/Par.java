package JyCSP;

import org.python.core.*;
/**
 * 
 * @author Sam Wilson, Sarah Mount
 * @version 1.0
 * 
 *  Java representation of the Jython Class Pae.
 * 
 * 
 * 
 */
public class Par extends PyObject implements JyCspParInterface {

	/**
	 * Java Seq Interface for the Jython Class Par.
	 */
	protected JyCspParInterface jcpi;
	
	/**
	 * Default constructor creates a Par Object
	 * 
	 * Makes a static call to CspFactory method creatJavaCspPar
	 * 
	 * @param args List of Processes
	 */
	public Par(JavaCspProcess...args){
		super();
		this.jcpi = CspFactory.createJavaCspPar(args);
	}

	/**
	 * Straight through method call to Par.run() (inherited method)
	 * Unknown behaviour
	 */
	public void run() {
		this.jcpi.run();
	}

	/**
	 * Straight through method call to Jython Par.start()
	 * 
	 * Starts the Par
	 */
	public void start() {
		this.jcpi.start();
	}

	/**
	 * Straight through method call to Jython Par.stop()
	 * 
	 * Stops the Par
	 * 
	 * Unknown behvaiour
	 */
	public void stop() {
		this.jcpi.stop();
	}
}
