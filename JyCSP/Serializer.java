package JyCSP;

import java.io.*;

public class Serializer {

	byte[] obj;

	boolean isempty = true;

	public Serializer() {
		super();
	}

	public void put(Object o) throws IOException {
		if(isempty){
		ByteArrayOutputStream b = new ByteArrayOutputStream();
		ObjectOutputStream oos = new ObjectOutputStream(b);
		oos.writeObject(o);
		this.obj = b.toByteArray();

		this.isempty = false;
		} else {
			return;
		}
	}

	public Object get() throws IOException, ClassNotFoundException {
		if (!isempty) {
			ByteArrayInputStream b = new ByteArrayInputStream(this.obj);
			ObjectInputStream ois = new ObjectInputStream(b);
			Object o = ois.readObject();

			this.isempty = true;
			return o;
		} else {
			return null;
		}
	}

}