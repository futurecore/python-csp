package JyCSP;

import org.python.core.PyObject;
import org.python.core.PyString;
import org.python.core.PyInteger;
import org.python.core.PyType;
import org.python.util.PythonInterpreter;

public class CspFactory {

	/**
	 * Handle on the Python Interpreter
	 */
	static PythonInterpreter interpreter = new PythonInterpreter();
	
	/**
	 * Flag if the class should print Debug information
	 * Default False
	 */
	static boolean debug = false;

	/**
	 * static Constructor
	 * Make a call to the interpreter to import Javacspthread 
	 */
	static {
		String cmd = "from Javacspthread import *";
		interpreter.exec(cmd);
	}

	/**
	 * Gets a handle to a Jython JCSPProcess object
	 * 
	 * @param i Class which implements the JavaCspProcessInterface,
	 * 			Similar to the Runnable interface.
	 * 
	 * 			If the user is extending JavaCspProcess this call is made
	 * 			by the constructor of the JavaCspProcess.
	 * 	
	 * 			If the user is implementing the JavaCspProcessInterface
	 * 			this method is analogous to Runnable interface, used with
	 * 			native java threads.
	 * 
	 * @return JyCspProcessInterface
	 */
	public static JyCspProcessInterface createJavaCspProcess(
			JavaCspProcessInterface i) {
		PyObject jyJCSPClass;
		jyJCSPClass = interpreter.get("JCSPProcess");
		PyObject JCSPObj = jyJCSPClass.__call__((PyObject)i);
		return (JyCspProcessInterface) JCSPObj
				.__tojava__(JyCspProcessInterface.class);
	}

	/**
	 * Gets a handle to a Jython Par Object
	 * 
	 * @param args  List of JavaCspProcesses which should be run in parallel
	 * 			   
	 * 				Users should avoid using this method, instead use
	 * 				the Java Par Class which makes a call to this
	 * @return
	 */
	public static JyCspParInterface createJavaCspPar(JavaCspProcess... args) {
		PyObject jyJCSPParClass;
		jyJCSPParClass = interpreter.get("ParFactory");
		PyObject JCSPObj = jyJCSPParClass.__call__((PyObject[])args);
		return (JyCspParInterface) JCSPObj
				.__tojava__(JyCspParInterface.class);
	}
	
	/**
	 * Gets a handle to a Jython Seq Object
	 * 
	 * @param args  List of JavaCspProcesses which should be run in sequence
	 * 			   
	 * 				Users should avoid using this method, instead use
	 * 				the Java Seq Class which makes a call to this
	 * @return
	 */
	public static JyCspSeqInterface createJavaCspSeq(JavaCspProcess... args) {
		PyObject jyJCSPSeqClass;
		jyJCSPSeqClass = interpreter.get("SeqFactory");
		PyObject JCSPObj = jyJCSPSeqClass.__call__((PyObject[])args);
		return (JyCspSeqInterface) JCSPObj
				.__tojava__(JyCspSeqInterface.class);
	}
	
	/**
	 * Gets a handle to a Jython Alt Object
	 * 
	 * @param args  List of Channels for the Alt to select from
	 * 			   
	 * 				Users should avoid using this method, instead use
	 * 				the Java Alt Class which makes a call to this
	 * @return JyCspAltInterface
	 */
	public static JyCspAltInterface createJavaCspAlt(JavaCspChannel... args) {
		PyObject jyJCSPAltClass;
		jyJCSPAltClass = interpreter.get("AltFactory");
		PyObject JCSPObj = jyJCSPAltClass.__call__((PyObject[])args);
		return (JyCspAltInterface) JCSPObj
				.__tojava__(JyCspAltInterface.class);
	}
	
	/**
	 * Gets a handle to a Jython Channel Object
	 * 
	 * @return JyCspChannelInterface
	 */
	public static JyCspChannelInterface createJavaCspChannel(){
		PyObject jyJCSPChannel;
		jyJCSPChannel = interpreter.get("Channel");
		PyObject JCSPObj = jyJCSPChannel.__call__();
		return (JyCspChannelInterface) JCSPObj
				.__tojava__(JyCspChannelInterface.class);
	}

}
