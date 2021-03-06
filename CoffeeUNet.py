import tensorflow as tf


def conv2d_t(x, filters, kernel_initializer, kernel_regularizer, bias_initializer):
    x = tf.keras.layers.Conv2DTranspose(
        filters=filters,
        kernel_size=(3, 3),
        strides=(2, 2),
        kernel_initializer=kernel_initializer,
        kernel_regularizer=kernel_regularizer,
        bias_initializer=bias_initializer,
        padding='same')(x)

    return x


def conv2d(x, filters, kernel_initializer, kernel_regularizer, bias_initializer, leaky_relu_alpha):
    x = tf.keras.layers.Conv2D(
        filters=filters,
        kernel_size=(3, 3),
        kernel_initializer=kernel_initializer,
        kernel_regularizer=kernel_regularizer,
        bias_initializer=bias_initializer,
        padding='same')(x)
    x = tf.keras.layers.LeakyReLU(alpha=leaky_relu_alpha)(x)
    x = tf.keras.layers.BatchNormalization()(x)

    x = tf.keras.layers.Conv2D(
        filters=filters,
        kernel_size=(3, 3),
        kernel_initializer=kernel_initializer,
        kernel_regularizer=kernel_regularizer,
        bias_initializer=bias_initializer,
        padding='same')(x)
    x = tf.keras.layers.LeakyReLU(alpha=leaky_relu_alpha)(x)
    x = tf.keras.layers.BatchNormalization()(x)

    return x


def create_model(
        input_shape=(128, 128, 1),
        num_layers=4,
        filters=16,
        num_classes=1,
        kernel_initializer='he_normal',
        kernel_regularizer=tf.keras.regularizers.l2(0.01),
        bias_initializer=tf.keras.initializers.Constant(value=0.1),
        leaky_relu_alpha=0.01,
        output_activation='sigmoid'):

    image_input = tf.keras.Input(shape=input_shape, name='img_input', dtype=tf.float32)
    x = tf.keras.layers.BatchNormalization()(image_input)

    down_layers = []
    for _ in range(num_layers):
        x = conv2d(x, filters, kernel_initializer, kernel_regularizer, bias_initializer, leaky_relu_alpha)
        down_layers.append(x)
        x = tf.keras.layers.MaxPooling2D((2, 2))(x)

        filters *= 2

    x = conv2d(x, filters, kernel_initializer, kernel_regularizer, bias_initializer, leaky_relu_alpha)

    for conv in reversed(down_layers):
        filters //= 2
        x = conv2d_t(x, filters, kernel_initializer, kernel_regularizer, bias_initializer)
        x = tf.keras.layers.concatenate([x, conv])
        x = conv2d(x, filters, kernel_initializer, kernel_regularizer, bias_initializer, leaky_relu_alpha)

    out = tf.keras.layers.Conv2D(
        filters=num_classes,
        kernel_size=(1, 1),
        kernel_initializer=kernel_initializer,
        kernel_regularizer=kernel_regularizer,
        bias_initializer=bias_initializer,
        activation=output_activation,
        name='map_output')(x)

    model = tf.keras.Model(inputs=[image_input], outputs=[out])
    return model
