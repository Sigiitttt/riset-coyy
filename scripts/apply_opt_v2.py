import json

fpath = 'kode/5_segmentasi_unet/sk3_bigdat_ham2019_unetmask_ak85_v2 (1).ipynb'
with open(fpath, encoding='utf-8') as f:
    nb = json.load(f)

# 1. Update Cell 16 (Streamlined Classifier Head)
c16 = ''.join(nb['cells'][16]['source'])
old_head = """    x = BatchNormalization()(x)

    x = Dense(512, activation='relu', kernel_regularizer=l2(0.001))(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu', kernel_regularizer=l2(0.001))(x)
    x = Dropout(0.4)(x)"""

new_head = """    x = BatchNormalization()(x)

    # Streamlined Classifier Head (Anti-Overfitting, Less Parameter Bloat)
    x = Dense(256, activation='relu', kernel_regularizer=l2(1e-4))(x)
    x = Dropout(0.35)(x)
    x = Dense(128, activation='relu', kernel_regularizer=l2(1e-4))(x)
    x = Dropout(0.25)(x)"""

if old_head in c16:
    c16 = c16.replace(old_head, new_head)
    nb['cells'][16]['source'] = c16.splitlines(keepends=True)
    print("Cell 16 head successfully updated!")
else:
    print("Old head pattern not found in Cell 16!")

# 2. Update Cell 18 (Soft Square-Root Class Weighting)
c18 = ''.join(nb['cells'][18]['source'])

target_insert = "print('[INFO] Memulai Fase 1: Warm-up Custom Head (5 Epoch)...')"
soft_weights_code = """# Hitung Soft Square-Root Class Weighting
# Formula w_i = sqrt(N_max / N_i) menaikkan recall Melanoma & BKL tanpa merusak presisi
counts = np.bincount(train_data.classes)
max_c = np.max(counts)
soft_weights = np.sqrt(max_c / counts)
soft_class_weights = {i: float(w) for i, w in enumerate(soft_weights)}

print("=== SOFT CLASS WEIGHTS (SQUARE-ROOT BALANCING) ===")
for cls, idx in sorted(train_data.class_indices.items(), key=lambda x: x[1]):
    print(f"  {cls:<22}: bobot {soft_class_weights[idx]:.3f}")
print("==================================================\\n")

print('[INFO] Memulai Fase 1: Warm-up Custom Head (5 Epoch)...')"""

if target_insert in c18:
    c18 = c18.replace(target_insert, soft_weights_code)
    c18 = c18.replace("    callbacks=callbacks_list\n)\n\nwaktu_f1", "    callbacks=callbacks_list,\n    class_weight=soft_class_weights\n)\n\nwaktu_f1")
    c18 = c18.replace("    callbacks=callbacks_list\n)\n\nwaktu_f2", "    callbacks=callbacks_list,\n    class_weight=soft_class_weights\n)\n\nwaktu_f2")
    nb['cells'][18]['source'] = c18.splitlines(keepends=True)
    print("Cell 18 successfully updated!")
else:
    print("Target insert not found in Cell 18!")

# 3. Update Cell 20 (Add TTA Evaluation in Step 4)
c20 = ''.join(nb['cells'][20]['source'])
old_blind_test = """# ----------------------------------------------------
# 4. BLIND TEST & EVALUASI TEST SET
# ----------------------------------------------------
print("\\n[INFO] Mengevaluasi Test Set (Blind Test)...")
test_data.reset()

Y_pred_test = best_model.predict(
    test_data, steps=len(test_data), verbose=0
)

y_pred_classes_test = np.argmax(Y_pred_test, axis=1)"""

new_blind_test = """# ----------------------------------------------------
# 4. BLIND TEST & EVALUASI TEST SET (STANDARD + TTA)
# ----------------------------------------------------
print("\\n[INFO] Mengevaluasi Test Set (Standard Predict)...")
test_data.reset()

Y_pred_standard = best_model.predict(
    test_data, steps=len(test_data), verbose=0
)
y_pred_classes_std = np.argmax(Y_pred_standard, axis=1)
y_true_test = np.array(test_data.classes)

from sklearn.metrics import accuracy_score
acc_std = accuracy_score(y_true_test, y_pred_classes_std)
print(f"Akurasi Standar Test: {acc_std * 100:.2f}%")

print("\\n[INFO] Menjalankan Test-Time Augmentation (TTA 4-Way Flip/Rot)...")
# TTA: Rata-rata prediksi dari 4 orientasi lesi (Original, Horizontal Flip, Vertical Flip, Rot90)
preds_tta = []
test_data.reset()
for batch_idx in range(len(test_data)):
    bx, _ = test_data[batch_idx]
    p1 = best_model(bx, training=False).numpy()
    p2 = best_model(tf.image.flip_left_right(bx), training=False).numpy()
    p3 = best_model(tf.image.flip_up_down(bx), training=False).numpy()
    p4 = best_model(tf.image.rot90(bx, k=1), training=False).numpy()
    preds_tta.append((p1 + p2 + p3 + p4) / 4.0)

Y_pred_test = np.vstack(preds_tta)
y_pred_classes_test = np.argmax(Y_pred_test, axis=1)
acc_tta = accuracy_score(y_true_test, y_pred_classes_test)
print(f"Akurasi TTA Test    : {acc_tta * 100:.2f}% (Delta: {acc_tta - acc_std:+.2%})")"""

if old_blind_test in c20:
    c20 = c20.replace(old_blind_test, new_blind_test)
    nb['cells'][20]['source'] = c20.splitlines(keepends=True)
    print("Cell 20 TTA successfully updated!")
else:
    print("old_blind_test not found in Cell 20!")

with open(fpath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Semua pembaruan berhasil disimpan ke notebook!")
