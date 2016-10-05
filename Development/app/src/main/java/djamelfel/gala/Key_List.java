package djamelfel.gala;

import android.os.Parcel;
import android.os.Parcelable;

import java.io.Serializable;

/**
 * Created by djamel on 17/10/15.
 */
public class Key_List implements Parcelable, Serializable {
    int id;
    String key;

    public Key_List(int id, String key) {
        this.id = id;
        this.key = key;
    }

    protected Key_List(Parcel in) {
        this.id = in.readInt();
        this.key = in.readString();
    }

    public int getId() {
        return this.id;
    }

    public String getKey() {
        return this.key;
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(this.id);
        dest.writeString(this.key);
    }


    public static final Creator<Key_List> CREATOR = new Creator<Key_List>() {
        @Override
        public Key_List createFromParcel(Parcel in) {
            return new Key_List(in);
        }

        @Override
        public Key_List[] newArray(int size) {
            return new Key_List[size];
        }
    };
}
