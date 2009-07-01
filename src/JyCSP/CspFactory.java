package JyCSP;

import org.python.core.PyObject;
import org.python.core.PyString;
import org.python.core.PyInteger;
import org.python.core.PyType;
import org.python.util.PythonInterpreter;

public class CspFactory {

	static PythonInterpreter interpreter = new PythonInterpreter();
	
	static boolean debug = false;

	static {
		String cmd = "from Javacspthread import *";
		interpreter.exec(cmd);
	}

	public static JyCspProcessInterface createJavaCspProcess(
			JavaCspProcessInterface i) {
		PyObject jyJCSPClass;
		jyJCSPClass = interpreter.get("JCSPProcess");
		PyObject JCSPObj = jyJCSPClass.__call__((PyObject)i);
		return (JyCspProcessInterface) JCSPObj
				.__tojava__(JyCspProcessInterface.class);
	}

	public static JyCspParInterface createJavaCspPar(JavaCspProcess... args) {
		PyObject jyJCSPParClass;
		jyJCSPParClass = interpreter.get("ParFactory");
		PyObject JCSPObj = jyJCSPParClass.__call__((PyObject[])args);
		return (JyCspParInterface) JCSPObj
				.__tojava__(JyCspParInterface.class);
	}
	
	public static JyCspSeqInterface createJavaCspSeq(JavaCspProcess... args) {
		PyObject jyJCSPSeqClass;
		jyJCSPSeqClass = interpreter.get("SeqFactory");
		PyObject JCSPObj = jyJCSPSeqClass.__call__((PyObject[])args);
		return (JyCspSeqInterface) JCSPObj
				.__tojava__(JyCspSeqInterface.class);
	}
	
	public static JyCspAltInterface createJavaCspAlt(JavaCspChannel... args) {
		PyObject jyJCSPAltClass;
		jyJCSPAltClass = interpreter.get("AltFactory");
		PyObject JCSPObj = jyJCSPAltClass.__call__((PyObject[])args);
		return (JyCspAltInterface) JCSPObj
				.__tojava__(JyCspAltInterface.class);
	}
	
	public static JyCspChannelInterface createJavaCspChannel(){
		PyObject jyJCSPChannel;
		jyJCSPChannel = interpreter.get("Channel");
		PyObject JCSPObj = jyJCSPChannel.__call__();
		return (JyCspChannelInterface) JCSPObj
				.__tojava__(JyCspChannelInterface.class);
	}

}
