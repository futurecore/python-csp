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
		ProcessStore.store.put(i.toString(), i);
		if (debug) {
			System.out.println("CspFactory output: Store size: "
					+ ProcessStore.store.size());
		}
		PyObject JCSPObj = jyJCSPClass.__call__(new PyString(i.toString()));
		return (JyCspProcessInterface) JCSPObj
				.__tojava__(JyCspProcessInterface.class);
	}

	public static JyCspParInterface createJavaCspPar(JavaCspProcess... args) {
		PyObject jyJCSPParClass;
		PyString[] n = new PyString[args.length];
		jyJCSPParClass = interpreter.get("ParFactory");
		for (int i = 0; i < args.length; i++) {
			ProcessStore.store.put(args[i].toString(),args[i]);
			n[i] = new PyString(args[i].toString());
		}
		if (debug) {
			System.out.println("CspFactory output: Store size: "
					+ ProcessStore.store.size());
		}
		PyObject JCSPObj = jyJCSPParClass.__call__(n);
		return (JyCspParInterface) JCSPObj
				.__tojava__(JyCspParInterface.class);
	}
	
	public static JyCspSeqInterface createJavaCspSeq(JavaCspProcess... args) {
		PyObject jyJCSPSeqClass;
		PyString[] n = new PyString[args.length];
		jyJCSPSeqClass = interpreter.get("SeqFactory");
		for (int i = 0; i < args.length; i++) {
			ProcessStore.store.put(args[i].toString(),args[i]);
			n[i] = new PyString(args[i].toString());
		}
		if (debug) {
			System.out.println("CspFactory output: Store size: "
					+ ProcessStore.store.size());
		}
		PyObject JCSPObj = jyJCSPSeqClass.__call__(n);
		return (JyCspSeqInterface) JCSPObj
				.__tojava__(JyCspSeqInterface.class);
	}

}
