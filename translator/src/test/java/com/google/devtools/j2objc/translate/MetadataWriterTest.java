/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.devtools.j2objc.translate;

import com.google.devtools.j2objc.GenerationTest;

import java.io.IOException;

/**
 * Unit tests for {@link MetadataWriter}.
 *
 * @author Keith Stanger
 */
public class MetadataWriterTest extends GenerationTest {

  public void testConstructorsHaveNullJavaName() throws IOException {
    String translation = translateSourceFile("class Test {}", "Test", "Test.m");
    assertTranslatedLines(translation,
        "static const J2ObjcMethodInfo methods[] = {",
        // The fourth field, "javaNameIdx", should be -1.
        "{ \"init\", NULL, 0x0, -1, -1, -1 },");
  }

  public void testMethodMetadata() throws IOException {
    String translation = translateSourceFile(
        // Separate methods are used so each only has one modifier.
        "abstract class Test<T> { "
        + " Object test1() { return null; }"  // package-private
        + " private char test2() { return 'a'; }"
        + " protected void test3() { }"
        + " final long test4() { return 0L; }"
        + " synchronized boolean test5() { return false; }"
        + " String test6(String s, Object... args) { return null; }"
        + " native void test7() /*-[ exit(0); ]-*/; "
        + " abstract void test8() throws InterruptedException, Error; "
        + " abstract T test9();"
        + " abstract void test10(int i, T t);"
        + " abstract <V,X> void test11(V one, X two, T three);"
        + "}",
        "Test", "Test.m");
    assertTranslation(translation, "{ \"test1\", \"Ljava.lang.Object;\", 0x0, -1, -1, -1 },");
    assertTranslation(translation, "{ \"test2\", \"C\", 0x2, -1, -1, -1 },");
    assertTranslation(translation, "{ \"test3\", \"V\", 0x4, -1, -1, -1 },");
    assertTranslation(translation, "{ \"test4\", \"J\", 0x10, -1, -1, -1 },");
    assertTranslation(translation, "{ \"test5\", \"Z\", 0x20, -1, -1, -1 },");
    assertTranslation(translation,
        "{ \"test6WithNSString:withNSObjectArray:\", \"Ljava.lang.String;\", 0x80, 0, -1, -1 }");
    assertTranslation(translation, "{ \"test7\", \"V\", 0x100, -1, -1, -1 },");
    assertTranslation(translation, "{ \"test8\", \"V\", 0x400, -1, 1, -1 },");
    assertTranslation(translation, "{ \"test9\", \"TT;\", 0x400, -1, -1, 2 },");
    assertTranslation(translation, "{ \"test10WithInt:withId:\", \"V\", 0x400, 3, -1, 4 },");
    assertTranslation(translation, "{ \"test11WithId:withId:withId:\", \"V\", 0x400, 5, -1, 6 },");
    assertTranslation(translation,
        "static const void *ptrTable[] = { \"test6\", "
        + "\"Ljava.lang.InterruptedException;Ljava.lang.Error;\", \"()TT;\", \"test10\", "
        + "\"(ITT;)V\", \"test11\", \"<V:Ljava/lang/Object;X:Ljava/lang/Object;>(TV;TX;TT;)V\" };");
  }

  public void testAnnotationMetadata() throws IOException {
    String translation = translateSourceFile(
        "import java.lang.annotation.*; @Retention(RetentionPolicy.RUNTIME) @interface Test { "
        + " String foo() default \"bar\";"
        + " int num() default 5;"
        + "}",
        "Test", "Test.m");
    assertTranslation(translation,
        "{ \"foo\", \"Ljava.lang.String;\", 0x401, -1, -1, -1 },");
    assertTranslation(translation, "{ \"num\", \"I\", 0x401, -1, -1, -1 },");
  }

  public void testInnerClassesMetadata() throws IOException {
    String translation = translateSourceFile(
        " class A {"
        + "class B {"
        + "  class InnerInner{}}"
        + "static class C {"
        + "  Runnable test() {"
        + "    return new Runnable() { public void run() {}};}}"
        + "interface D {}"
        + "@interface E {}"
        + "}"
        , "A", "A.m");
    assertTranslation(translation,
        "static const char *inner_classes[] = {\"LA$B;\", \"LA$C;\", \"LA$D;\", \"LA$E;\"};");
    assertTranslation(translation,
        "static const J2ObjcClassInfo _A = { 3, \"A\", NULL, NULL, 0x0, 1, methods, "
        + "0, NULL, 0, NULL, 4, inner_classes, NULL, NULL, NULL };");
  }

  public void testEnclosingMethodAndConstructor() throws IOException {
    String translation = translateSourceFile(
        "class A { A(String s) { class B {}} void test(int i, long l) { class C { class D {}}}}",
        "A", "A.m");
    assertTranslatedLines(translation,
        "static const J2ObjCEnclosingMethodInfo "
        + "enclosing_method = { \"A\", \"initWithNSString:\" };",
        "static const J2ObjcClassInfo _A_1B = { 3, \"B\", NULL, \"A\", 0x0, 1, methods, "
        + "0, NULL, 0, NULL, 0, NULL, &enclosing_method, NULL, NULL };");
    assertTranslatedLines(translation,
        "static const J2ObjCEnclosingMethodInfo "
        + "enclosing_method = { \"A\", \"testWithInt:withLong:\" };",
        "static const J2ObjcClassInfo _A_1C = { 3, \"C\", NULL, \"A\", 0x0, 1, methods, "
        + "0, NULL, 0, NULL, 1, inner_classes, &enclosing_method, NULL, NULL };");

    // Verify D is not enclosed by test(), as it's enclosed by C.
    assertTranslation(translation,
        "J2ObjcClassInfo _A_1C_D = { 3, \"D\", NULL, \"A$C\", 0x0, 1, methods, "
        + "0, NULL, 0, NULL, 0, NULL, NULL, NULL, NULL }");
  }
}
