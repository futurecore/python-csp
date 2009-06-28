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
		String cmd = "from Jycspthread import *";
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
	
	public static JyCspAltInterface createJavaCspAlt(JCspChannel... args) {
		PyObject jyJCSPAltClass;
		PyString[] n = new PyString[args.length];
		jyJCSPAltClass = interpreter.get("AltFactory");
		for (int i = 0; i < args.length; i++) {
			ProcessStore.store.put(args[i].toString(),args[i]);
			n[i] = new PyString(args[i].toString());
		}
		if (debug) {
			System.out.println("CspFactory output: Store size: "
					+ ProcessStore.store.size());
		}
		PyObject JCSPObj = jyJCSPAltClass.__call__(n);
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
