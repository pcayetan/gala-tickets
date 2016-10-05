package djamelfel.gala;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.JsonHttpResponseHandler;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Iterator;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import cz.msebera.android.httpclient.Header;
import cz.msebera.android.httpclient.entity.StringEntity;


public class Read_QR_Code extends ActionBarActivity implements View.OnClickListener {

    static final String ACTION_SCAN = "com.google.zxing.client.android.SCAN";
    private ArrayList<Key_List> key_list = null;
    private String server;
    private EditText _nbrPlace;
    private EditText _barCode;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_read__qr__code);

        Intent intent = getIntent();
        if (intent != null) {
            key_list = intent.getParcelableArrayListExtra("key_list");
            server = intent.getStringExtra("server");
        }

        _nbrPlace = (EditText)findViewById(R.id.id_nbrPlace);
        _nbrPlace.setText("1", TextView.BufferType.EDITABLE);

        _barCode = (EditText)findViewById(R.id.barCode);

        Button buttonBarCode = (Button) findViewById(R.id.ButtonBarCode);
        buttonBarCode.setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        switch(v.getId()) {
            case R.id.ButtonBarCode :
                // Save and Reset to default code bar
                String str = _barCode.getText().toString();
                //_barCode.setText("", TextView.BufferType.EDITABLE);

                if (str.isEmpty()) {
                    display(getString(R.string.empty_text_area), false);
                }
                else {
                    validateTicket(str);
                }
                break;
        }
    }

    public void scanQR(View v) {
        if (key_list == null) {
            display(getString(R.string.error_lib_empty), false);
            return;
        }
        try {
            Intent intent = new Intent(ACTION_SCAN);
            startActivityForResult(intent, 1);
        } catch (ActivityNotFoundException anfe) {
            showDialog(Read_QR_Code.this, getString(R.string.noQRCodeApplication), getString(R
                    .string.downloadQRCode), "Oui", "Non").show();
        }
    }

    private static AlertDialog showDialog(final Activity act, CharSequence title, CharSequence
            message, CharSequence buttonYes, CharSequence buttonNo) {
        AlertDialog.Builder downloadDialog = new AlertDialog.Builder(act);
        downloadDialog.setTitle(title);
        downloadDialog.setMessage(message);
        downloadDialog.setPositiveButton(buttonYes, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialogInterface, int i) {
                Uri uri = Uri.parse("market://search?q=pname:" + "com.google.zxing.client.android");
                Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                try {
                    act.startActivity(intent);
                } catch (ActivityNotFoundException anfe) {

                }
            }
        });
        downloadDialog.setNegativeButton(buttonNo, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialogInterface, int i) {
            }
        });
        return downloadDialog.show();
    }

    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        if (resultCode == RESULT_OK) {
            String contents = intent.getStringExtra("SCAN_RESULT");

            validateTicket(contents);
        }
    }

    public void validateTicket(String result) {
        final String str[] = result.split(" ");
        int nbrPlaceSelect = Integer.parseInt(_nbrPlace.getText().toString());
        int nbrPlaceTot = Integer.parseInt(str[2]);
        Boolean idFound = false;

        // Reset to default number of place
        _nbrPlace.setText("1", TextView.BufferType.EDITABLE);

        if (Integer.parseInt(str[2]) < nbrPlaceSelect) {
            display(getString(R.string.nbPlaceOversize), false);
            return;
        }

        Iterator<Key_List> itr = key_list.iterator();
        while (itr.hasNext()) {
            Key_List key = itr.next();

            if (key.getId() == Integer.parseInt(str[1])) {
                // generate HMAC in hex
                String hmac = hmacDigest(str[0]+" "+str[1]+" "+str[2], key.getKey(), "HmacSHA1");

                if(str[3].equals(hmac.substring(0, str[3].length()).toUpperCase())) {
                    // Ticket is valid
                    idFound = true;

                    JSONObject jsonParams = new JSONObject();
                    StringEntity entity = null;

                    try {
                        // Set parameters in JSON structure
                        jsonParams.put("verif", str[3]);
                        jsonParams.put("nb", nbrPlaceSelect);
                        jsonParams.put("qt", nbrPlaceTot);

                        // Set JSON parameters for Post request
                        entity = new StringEntity(jsonParams.toString());


                    } catch (JSONException e) {
                        e.printStackTrace();
                    } catch (UnsupportedEncodingException e) {
                        e.printStackTrace();
                    }

                    // Send Post Request
                    AsyncHttpClient client = new AsyncHttpClient();
                    client.post(this, server + "/validate", entity, "application/json",
                            new JsonHttpResponseHandler() {
                        @Override
                        public void onSuccess(int statusCode, Header[] headers, JSONArray response) {
                            Log.i("debug", "toto ");
                            Log.i("debug", response.toString());
                        }

                        @Override
                        public void onFailure(int statusCode, Header[] headers, String responseString, Throwable throwable) {
                            display(getString(R.string.serverError), false);
                        }

                        @Override
                        public void onFailure(int statusCode, Header[] headers, Throwable throwable, JSONObject errorResponse) {
                            display(getString(R.string.serverError), false);
                        }

                        @Override
                        public void onFailure(int statusCode, Header[] headers, Throwable throwable, JSONArray errorResponse) {
                            display(getString(R.string.serverError), false);
                        }
                    });
                }
            }
        }
        if (!idFound) {
            display(getString(R.string.ebillet_false), false);
        }
    }

    /**
     *
     * @param msg
     * @param success
     * @info print on screen a message in red if success in false or green if it's true
     */
    public void display(String msg, boolean success) {
        LayoutInflater inflater = getLayoutInflater();
        View layout;
        if(success) {
            layout = inflater.inflate(R.layout.toast_success,
                    (ViewGroup) findViewById(R.id.toast_success));
        }
        else {
            layout = inflater.inflate(R.layout.toast_failure,
                    (ViewGroup) findViewById(R.id.toast_failure));
        }
        TextView text = (TextView)layout.findViewById(R.id.text);
        text.setTextSize(20);
        text.setText(msg.toUpperCase());

        Toast toast = new Toast(getApplicationContext());
        toast.setDuration(Toast.LENGTH_LONG);
        toast.setView(layout);
        toast.show();
    }

    /**
     *
     * @param msg
     * @param keyString
     * @param algo
     * @return hmac in hex from a message, a key and an algorithm
     */
    public static String hmacDigest(String msg, String keyString, String algo) {
        String digest = null;
        try {
            SecretKeySpec key = new SecretKeySpec((keyString).getBytes("UTF-8"), algo);
            Mac mac = Mac.getInstance(algo);
            mac.init(key);

            byte[] bytes = mac.doFinal(msg.getBytes("ASCII"));

            StringBuffer hash = new StringBuffer();
            for (int i = 0; i < bytes.length; i++) {
                String hex = Integer.toHexString(0xFF & bytes[i]);
                if (hex.length() == 1) {
                    hash.append('0');
                }
                hash.append(hex);
            }
            digest = hash.toString();
        } catch (UnsupportedEncodingException e) {
        } catch (InvalidKeyException e) {
        } catch (NoSuchAlgorithmException e) {
        }
        return digest;
    }
}
