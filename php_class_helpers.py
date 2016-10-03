#from .commands.add_dependency import AddDependencyCommand
import sublime
import sublime_plugin

class AddDependencyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.step_one()
        
    def step_one(self):
        self.view.window().show_input_panel('property name:', '', self.step_two, None, None)

    def step_two(self, user_input):
        self.property_name = user_input
        self.step_three()

    def step_three(self):
        self.view.window().show_input_panel('class name:', '', self.step_four, None, None)

    def step_four(self, user_input):
        self.class_name = user_input
        self.view.run_command('add_dependency_run', {'property_name': self.property_name, 'class_name': self.class_name})

class AddDependencyRunCommand(sublime_plugin.TextCommand):
    'Inserts a constructor argument that sets a property.'

    def description(self):
        'The description of the command.'
        return 'Insert a constructor argument.'

    def run(self, edit, property_name, class_name):
        'Run the command.'
        self.edit = edit
        self.add_property(property_name, class_name)
        self.add_constructor()
        self.add_constructor_param(property_name, class_name)
        self.add_constructor_property_setter(property_name)
        self.find_use(class_name)
        self.update_constructor_docblock()
        
    def add_property(self, prop_name, class_name):
        text = "\n\t" + "/**\n\t * @var " + class_name + "\n\t */\n\t" + 'private' + " $" + prop_name + ";"
        self.view_insert(self.find_first_available_position(), text)

    def add_constructor(self):
        if not self.view.find(r'__construct\s*\(', 0):
            text = "\n\tpublic function __construct()\n\t{\n\t}"
            if len(self.find_methods()) > 0:
                text += "\n\t"
            self.view_insert(self.find_first_available_position(), text)

    def add_constructor_param(self, prop_name, class_name):
        param_definition = class_name + " $" + prop_name
        param_separator = ""
        
        constructor_params_position = self.find_constructor_params()
        constructor_args = self.view.substr(constructor_params_position)
        new_arg_position = constructor_params_position.end()

        if constructor_args.strip() != '':
            param_separator = ", "

        if self.is_multiline_constructor():
            new_arg_position = self.view.find_by_class(constructor_params_position.end(), False, sublime.CLASS_LINE_END)
            param_separator = param_separator.strip() + "\n\t\t"

        self.view_insert(new_arg_position, param_separator + param_definition)

    def add_constructor_property_setter(self, prop_name):
        constructor_params_position = self.find_constructor_params()
        constructor_close = self.view.find(r'\}', constructor_params_position.end()).begin()
        last_newline = self.view.find_by_class(constructor_close, False, sublime.CLASS_LINE_START)
        self.view_insert(last_newline, "\t\t$this->" + prop_name + ' = $' + prop_name + ";\n")

    def find_use(self, class_name):
        sel = self.view.sel()
        sel.clear()
        sel.add(self.view.find(class_name, 0).begin())
        self.view.run_command("find_use")
        sel.clear()

    def update_constructor_docblock(self):
        consructor_docblock_pos = self.find_method_docblock('__construct')

        if consructor_docblock_pos.begin() > 0:
            self.delete_region(consructor_docblock_pos)

        const_pos = self.view.find('public function __construct\s*\(', 0).begin()
        self.view_insert(const_pos, '\n\t')
        const_pos += self.view_insert(const_pos, '/**')
        self.view_set_selection(const_pos)
        self.view.run_command('jsdocs')
        self.view_clear_selection()

    def find_class_opening_bracket(self):
        pos = self.view.find(r'class\s+[0-9A-Za-z_]+', 0).end()
        return self.view.find(r'\{', pos).end()

    def find_properties(self):
        return self.view.find_all(r'(public|protected|private)\s+\$[A-Za-z_]+;')

    def find_methods(self):
        return self.view.find_all(r'(public|protected|private) function')

    def view_insert(self, pos, text):
        return self.view.insert(self.edit, pos, text)

    def view_set_selection(self, pos):
        self.view_clear_selection()
        self.view.sel().add(pos)

    def view_clear_selection(self):
        self.view.sel().clear()

    def delete_region(self, region):
        self.view.erase(self.edit, region)

    def find_method_docblock(self, method_name, delete_empty_line = True):
        begin_pos = self.view.find('/\*\*[^/]+\*/[\n \t]*(public|protected|private) function ' + method_name + '\(', 0).begin()
        end_pattern = '\*/'
        if delete_empty_line:
            end_pattern += '[\n \t]*'
        end_pos = self.view.find(end_pattern, begin_pos).end()
        return sublime.Region(begin_pos, end_pos)

    def find_first_available_position(self):
        properties = self.find_properties()

        if properties:
            pos = properties[-1].end()
            pos += self.view_insert(pos, "\n\t")
        else:
            pos = self.find_class_opening_bracket()

        return pos

    def find_constructor_params(self):
        constructor = self.view.find(r'__construct\s*\(', 0)
        constructor_params_start = constructor.end()
        constructor_params_end = self.view.find(r'\)', constructor_params_start).begin()
        return sublime.Region(constructor_params_start, constructor_params_end)

    def is_multiline_constructor(self):
        params_end = self.find_constructor_params().end()
        last_newline = self.view.find_by_class(params_end, False, sublime.CLASS_LINE_END)
        last_word = self.view.find_by_class(params_end, False, sublime.CLASS_SUB_WORD_START)
        return last_newline > last_word