package JyCSP.util;

import java.io.*;

public class Serializer {

	/**
	 * Serialized Object Store
	 */
	byte[] obj;

	/**
	 * Defines if the Serialized object store contains a
	 * serialized representation of a Java Object
	 */
	boolean isempty = true;

	/**
	 * Default Constructor
	 */
	public Serializer() {
		super();
	}

	/**
	 * Serializes the Object and stores the object in the Objects store
	 * @param o Object to Serialize
	 * @throws IOException
	 */
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

	/**
	 * Retrieves the Object from the object store, Type is preserved although
	 * a cast is necessary
	 */
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