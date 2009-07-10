package JyCSP;

import org.python.core.*;
import org.python.core.PyObject;

/**
 * 
 * @author Sam Wilson, Sarah Mount
 * @version 1.0
 * 
 *  Java representation of the Jython Class Channel.
 *  
 * CSP Channel objects.

 * In csp there are two sorts of channel. In CSP terms these
 * are Any2Any, Alting channels. However, each channel creates an
 * operating system level pipe. Since this is a file object the
 * number of channels a program can create is limited to the maximum
 * number of files the operating system allows to be open at any one
 * time. To avoid this bottleneck use L{FileChannel} objects, which
 * close the file descriptor used for IPC after every read or write
 * operations. Read and write operations are, however, over 20 time
 * lower when performed on L{FileChannel} objects.
 * 
 * 
 */
public class JavaCspChannel extends PyObject implements JyCspChannelInterface{
	
	/**
	 * Java Channel Interface for the Jython Class Channel.
	 */
	protected JyCspChannelInterface jcsi;
	
	/**
	 * Name of the channel
	 */
	public String name;
	

	/**
	 * Default Constructor
	 * 
	 * Makes a call to the static method createJavaCspChannel in the
	 * CspFactory
	 */
	public JavaCspChannel(){
		super();
		this.jcsi = CspFactory.createJavaCspChannel();
	}

	/**
	 * Straight through call to Channel.write()
	 * 
	 * Writes an object to the Channel
	 * 
	 * Channel.write uses the Serializer Class. if an object is to be
	 * serialized correctly ensure that your class implements serializable
	 */
	public void write(Object o){
		this.jcsi.write(o);
	}
	
	/**
	 * Straight through call to Channel.read()
	 * 
	 * Reads the object stored in the channel
	 * 
	 * The Type of the object written to teh channel is preserved,
	 * A type cast is required.
	 */
	public Object read(){
		return this.jcsi.read();
	}
	
	/**
	 * Straight through call to Channel.poison()
	 * 
	 * Poisons the channel
	 */
	public void poison(){
		this.jcsi.poison();
	}
	
	/**
	 * Straight through call to Channel.select()
	 * 
	 * Completes a channel read
	 * 
	 * @return the object written to the channel 
	 */
	public Object select(){
		return this.jcsi.select();
	}
	
	/**
	 * Straight through call to Channel.disable()
	 * 
	 * Disables this channel for alting
	 * 
	 */
	public void disable(){
		this.jcsi.disable();
	}
	
	/**
	 * Straight through call to Channel.enable()
	 * 
	 * Enables this channel for alting
	 */
	public void enable(){
		this.jcsi.enable();
	}
	
	/**
	 * Unknown behaviour
	 */
	public boolean is_selected(){
		return this.jcsi.is_selected();
	}
	
	/**
	 * Straight through call to Channel.is_selectable()
	 * 
	 * @return if the channel is selectable
	 */
	public boolean is_selectable(){
		return this.jcsi.is_selectable();
	}


}
